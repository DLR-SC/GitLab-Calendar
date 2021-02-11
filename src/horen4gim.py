"""
Extension for GitLab, that generates ics-files from a repositories issues,
 milestones and iterations, which have a due date.
"""

import os
import configparser
import sys
import argparse
from pathlib import Path
import gitlab
from gitlab.v4.objects import ProjectIssue, ProjectMilestone, GroupIssue, GroupMilestone
from ics import Calendar, Event


def connect_to_gitlab(config_path="", server_url="", private_access_token=""):
    """
    personal access token authentication
    """
    if config_path:
        gila = gitlab.Gitlab.from_config("dlr", config_files=config_path)
    else:
        gila = gitlab.Gitlab(server_url, private_token=private_access_token)
    gila.auth()
    return gila


def get_project(gila, project_id):
    """
    returns a specific project from a given ID
    """
    instance = gila.projects.get(project_id)
    return instance


def get_group(gila, group_id):
    """
    returns a specific group from a given ID
    """
    instance = gila.groups.get(group_id)
    return instance


def get_events(instance, api_endpoints, filters):
    """
    for each given terminated api_endpoint a calendar event is created
    """

    events = set()
    for item in api_endpoints.list(all=True, **filters):
        if item.due_date is not None:
            event = create_event(item, instance)
            events.add(event)
    return events


def create_event(todo, instance):
    """
    creates a new event and adds it to the calendar object
    """
    event = Event()
    # decision whether the todos are milestones or a issues
    if isinstance(todo, (GroupIssue, ProjectIssue)):
        event.name = "[" + instance.name + "] " + todo.title + " (ISSUE)"
        event.begin = todo.due_date
        event.categories.add("Issues")
        if todo.milestone is None:
            event.description = todo.description
        else:
            event.description = "From Milestone: " + todo.milestone.get("title") +\
                                "\n\n" + todo.description
    elif isinstance(todo, (GroupMilestone, ProjectMilestone)):
        event.name = "[" + instance.name + "] " + todo.title + " (MILESTONE)"
        event.begin = todo.due_date
        event.categories.add("Milestones")
        event.description = todo.description
    event.location = todo.web_url
    event.make_all_day()
    print(" TITLE: ", todo.title, "\tDUE_DATE: ", todo.due_date)
    return event


def create_calendar():
    """
    creates the calendar object
    """
    cal = Calendar()
    return cal


def write_calendar(calendar, file_path, name):
    """
    writes a calendar-file from a given calendar object
    """

    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(calendar)
    print("Successful creation of the file named \"" + name + "\".")


def write_calendars(calendars, target_path):
    """
    calls the "write_calendar" function for each given project
    """
    for calendar, name in calendars:
        name += ".ics"
        if calendar.events != set():
            write_calendar(calendar, target_path.joinpath(name), name)
        else:
            print("The Calendar called \"" + name +
                  "\" would be empty and is not going to be created")


def filter_todos(instance, only_issues, only_milestones):
    """
    from an instance the todos that the user wants are going to be stored in
    sets as events.
    """
    issue_events = set()
    milestone_events = set()

    if (only_issues is False and only_milestones is False) or \
            (only_issues is True and only_milestones is True):
        issue_events = get_events(instance, instance.issues, {"state": "opened"})
        milestone_events = get_events(instance, instance.milestones, {"state": "active"})
    elif only_issues is True and only_milestones is False:
        issue_events = get_events(instance, instance.issues, {"state": "opened"})
    elif only_issues is False and only_milestones is True:
        milestone_events = get_events(instance, instance.milestones, {"state": "active"})
    return issue_events, milestone_events


def convert_ids(id_string):
    """
    converts a string of given ids into a set of integer ids
    """
    if id_string != "":
        return {int(pid) for pid in id_string.split(',')}
    else:
        return set()


def converter(gila, project_ids=None, group_ids=None,
              only_issues=False, only_milestones=False,
              combined_calendar="", target_directory_path="."):
    """
    central function of the program
    """

    path = Path(target_directory_path)
    os.makedirs(path, exist_ok=True)
    if not path.exists():
        raise FileNotFoundError("There is no valid target directory path")

    if project_ids is None and group_ids is None:
        print("There are no ids given", file=sys.stderr)
        sys.exit(303)

    # get issues and milestones from either projects or groups
    groups = {}
    projects = {}

    for project_id in project_ids:
        project = get_project(gila, project_id)
        issue_events, milestone_events = filter_todos(project, only_issues, only_milestones)
        events = issue_events.union(milestone_events)
        projects[project.name] = events
    for group_id in group_ids:
        group = get_group(gila, group_id)
        issue_events, milestone_events = filter_todos(group, only_issues, only_milestones)
        events = issue_events.union(milestone_events)
        groups[group.name] = events

    # combined cal or many cals

    if combined_calendar and combined_calendar != "False":
        cal = create_calendar()
        all_events = merge_events(groups, projects)
        cal.events.update(all_events)
        write_calendar(cal, path.joinpath(combined_calendar), combined_calendar)
    else:
        calendars = []
        for project in projects:
            cal = create_calendar()
            cal.events.update(projects[project])
            calendars.append((cal, project))
        for group in groups:
            cal = create_calendar()
            cal.events.update(groups[group])
            calendars.append((cal, group))
        write_calendars(calendars, path)


def merge_events(groups, projects):
    all_events = set()
    all_events.update(*groups.values())
    for events in projects.values():
        for p_event in events:
            seen = False
            for a_event in all_events:
                if p_event.location == a_event.location:
                    seen = True
                    break
            if not seen:
                all_events.add(p_event)
    return all_events


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config",
                        default=None,
                        help="Path of your config. If you dont use a config, "
                             "you have to enter an url and authentication token manually",
                        type=str)
    parser.add_argument("-u", "--url",
                        default="https://gitlab.dlr.de",
                        help="Url of the gitlab instance you want to get your data from",
                        type=str)
    parser.add_argument("-t", "--token",
                        default=None,
                        help="Personal Access Token to the gitlab instance")
    parser.add_argument("-d", "--directory",
                        default="",
                        help="The directory where you want your calendar/s to be created",
                        type=str)
    parser.add_argument("-p", "--project", default=None,
                        help="All the IDs from Projects that you want,"
                             " separated by \",\"",
                        nargs='+')
    parser.add_argument("-g", "--group", default=None,
                        help="All the IDs from Groups that you want,"
                             " separated by \",\"",
                        nargs='+')
    parser.add_argument("-i", "--issues",
                        help="Only issues are noticed",
                        action="store_true")
    parser.add_argument("-m", "--milestones",
                        help="Only milestones are noticed",
                        action="store_true")
    parser.add_argument("-c", "--combine",
                        help="If you want to combine all files into one file,"
                             " you should append this to your command and"
                             "the wanted name of your file",
                        type=str)
    args = parser.parse_args()
    if args.config is None:
        raise Exception()
    try:
        config = configparser.ConfigParser()
        config.read(args.config)
        args.groups = convert_ids(config.get('horen4gim', 'GITLAB_GROUP_ID'))
        args.projects = convert_ids(config.get('horen4gim', 'GITLAB_PROJECT_ID'))
        args.issues = bool(config.get('horen4gim', 'ISSUES'))
        args.milestones = bool(config.get('horen4gim', 'MILESTONES'))
        args.combine = config.get('horen4gim', 'COMBINED_FILE', fallback="")
        args.directory = config.get('horen4gim', 'ABS_PATH')
    except configparser.NoSectionError as error:
        print("Config Missing", error)
    except configparser.NoOptionError as error:
        print("Option Missing", error)

    if not args.projects and not args.groups:
        print("There is no project or group id given", file=sys.stderr)
        sys.exit(606)

    gl = connect_to_gitlab(args.config, args.url, args.token)
    converter(gl, args.projects, args.groups, args.issues,
              args.milestones, args.combine, args.directory)
