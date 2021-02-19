"""
Extension for GitLab, that generates ics-files from a repositories issues,
 milestones and iterations, which have a due date.
"""

import os
import configparser
import argparse
from pathlib import Path
import gitlab
from gitlab.v4.objects import ProjectIssue, ProjectMilestone, GroupIssue, GroupMilestone
from ics import Calendar, Event


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
        if isinstance(todo, GroupIssue):
            project = api.projects.get(todo.project_id)
            event.name = "[" + project.name_with_namespace + "] " + todo.title + " (GROUP_ISSUE)"
        else:
            event.name = "[" + instance.name + "] " + todo.title + " (PROJECT_ISSUE)"
        event.begin = todo.due_date
        event.categories.add("Issues")
        if todo.milestone is None:
            event.description = todo.description
        else:
            event.description = "From Milestone: " + todo.milestone.get("title") + \
                                "\n\n" + todo.description
    elif isinstance(todo, (GroupMilestone, ProjectMilestone)):
        if isinstance(todo, GroupMilestone):
            event.name = "[" + instance.name + "] " + todo.title + " (GROUP_MILESTONE)"
        else:
            event.name = "[" + instance.name + "] " + todo.title + " (PROJECT_MILESTONE)"
        event.begin = todo.due_date
        event.categories.add("Milestones")
        event.description = todo.description

    event.location = todo.web_url
    event.make_all_day()
    print(" TITLE: ", todo.title, "\tDUE_DATE: ", todo.due_date)
    return event


def merge_events(groups, projects):
    """
    creates a set that includes all events from all projects and groups
    that are given
    :param groups:
    :param projects:
    :return:
    """
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


def filter_events(instance, only_issues, only_milestones):
    """
    from an instance the todos that the user wants are going to be stored in
    sets as events.
    """
    issue_events = set()
    milestone_events = set()

    if only_issues == only_milestones:
        issue_events = get_events(instance, instance.issues, {"state": "opened"})
        milestone_events = get_events(instance, instance.milestones, {"state": "active"})
    elif only_issues is True and only_milestones is False:
        issue_events = get_events(instance, instance.issues, {"state": "opened"})
    else:
        milestone_events = get_events(instance, instance.milestones, {"state": "active"})
    return issue_events, milestone_events


def convert_ids(id_string):
    """
    converts a string of given ids into a set of integer ids
    """
    ids = set()
    if id_string != "":
        for pid in id_string.split(','):
            try:
                ids.add(int(pid))
            except ValueError:
                print("\"" + pid + "\" is not a valid id.")
        return ids
    else:
        return None


def get_events_from_instances(gila, ids, id_type, only_issues, only_milestones):
    instances = {}
    for identification in ids:
        try:
            if id_type == "project":
                instance = gila.projects.get(identification)
            else:
                instance = gila.groups.get(identification)

            issue_events, milestone_events = filter_events(instance, only_issues, only_milestones)
            events = issue_events.union(milestone_events)
            instances[instance.name] = events
        except gitlab.GitlabGetError as err:
            print(str(identification) + " is not existing or the access is denied, please check again", err)
    return instances


def converter(gila, only_issues, only_milestones,
              project_ids=None, group_ids=None,
              combined_calendar="", target_directory_path="."):
    """
    central function of the program
    """

    path = Path(target_directory_path)
    os.makedirs(path, exist_ok=True)
    # get issues and milestones from either projects or groups
    groups = {}
    projects = {}
    print(project_ids, group_ids)
    if project_ids is None and group_ids is None:
        raise ValueError
    else:
        try:
            projects = get_events_from_instances(gila, project_ids, "project", only_issues, only_milestones)
            groups = get_events_from_instances(gila, group_ids, "group", only_issues, only_milestones)
        except TypeError as err:
            print("No ID given : ", err)
        except gitlab.GitlabHttpError as err:
            print("Not found ", err)
            pass

    # combined cal or many cals
    if combined_calendar:
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


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config",
                        default=None,
                        help="Path of your config. If you dont use a config, "
                             "you have to enter an url and authentication token manually",
                        type=str)
    parser.add_argument("-u", "--url",

                        help="Url of the gitlab instance you want to get your data from",
                        type=str)
    parser.add_argument("-t", "--token",
                        default=None,
                        help="Personal Access Token to the gitlab instance")
    parser.add_argument("-d", "--directory",
                        default="",
                        help="The directory where you want your calendar/s to be created",
                        type=str)
    parser.add_argument("-p", "--projects", default=None,
                        help="All the IDs from Projects that you want,"
                             " separated by \",\"",
                        nargs='+')
    parser.add_argument("-g", "--groups", default=None,
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
    arguments = parser.parse_args()
    return arguments


if __name__ == "__main__":
    args = parse_arguments()
    api = None
    if args.config:
        try:
            config = configparser.ConfigParser()
            config.read(args.config)
            api = gitlab.Gitlab.from_config("horen4gim", config_files=args.config)
            args.groups = convert_ids(config.get('horen4gim', 'GITLAB_GROUP_ID'))
            args.projects = convert_ids(config.get('horen4gim', 'GITLAB_PROJECT_ID'))
            args.issues = bool(config.get('horen4gim', 'ISSUES', fallback=False))
            args.milestones = bool(config.get('horen4gim', 'MILESTONES', fallback=False))
            args.combine = config.get('horen4gim', 'COMBINED_FILE', fallback="")
            args.directory = config.get('horen4gim', 'ABS_PATH')
        except TypeError as error:
            print("Config Missing", error)
        except configparser.NoSectionError as error:
            print("Section Missing", error)
        except configparser.NoOptionError as error:
            print("Option Missing", error)
        except configparser.DuplicateOptionError as error:
            print("Duplicate Option", error)
    else:
        api = gitlab.Gitlab(args.url, private_token=args.token)

    api.auth()
    converter(api, args.issues, args.milestones, args.projects,
              args.groups, args.combine, args.directory)
