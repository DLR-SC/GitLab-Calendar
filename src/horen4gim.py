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


def connect_to_gitlab(server_url, private_access_token):
    """
    personal access token authentication
    """
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


def get_events(api_endpoints, filters):
    """
    for each given terminated api_endpoint a calendar event is created
    """
    events = set()
    for item in api_endpoints.list(all=True, **filters):
        if item.due_date is not None:
            event = create_event(item)
            events.add(event)
    return events


def create_event(todo):
    """
    creates a new event and adds it to the calendar object
    """
    event = Event()

    # decision whether the todos are milestones or a issues
    if isinstance(todo, ProjectIssue) or isinstance(todo, GroupIssue):
        event.name = todo.title + " (ISSUE)"
        event.begin = todo.due_date
        event.categories.add("Issues")
        if todo.milestone is None:
            event.description = todo.description
        else:
            event.description = "From Milestone: " + todo.milestone.get("title") +\
                                "\n\n" + todo.description
    elif isinstance(todo, ProjectMilestone) or (isinstance(todo, GroupMilestone)):
        event.name = todo.title + " (MILESTONE)"
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
    print("Successful creation of the file named \"" + name + ".ics\".")


def write_calendars(calendars, target_path):
    """
    calls the "write_calendar" function for each given project
    """
    for calendar, name in calendars:
        if calendar.events != set():
            write_calendar(calendar, target_path.joinpath(name + '.ics'), name)
        else:
            print("The Calendar called \"" + name +
                  ".ics\" would be empty and is not going to be created")


def write_combined_cal(calendars, file_name):
    """
    writes a combined file with all the events
    """
    with open(file_name, 'w', encoding='utf-8') as combined_calendar_file:
        for calendar, name in calendars:
            combined_calendar_file.writelines(calendar)
        print("The Calendars were successfully combined.")


def fill_cal_object(instance, only_issues, only_milestones, cal):
    if (only_issues is False and only_milestones is False) or\
            (only_issues is True and only_milestones is True):
        cal.events.update(instance[0])
        cal.events.update(instance[1])
    elif only_issues is True and only_milestones is False:
        cal.events.update(instance[0])
    elif only_issues is False and only_milestones is True:
        cal.events.update(instance[1])
    # print(cal)
    return cal


def convert_ids(id_string):
    """
    converts a string of given ids into a set of integer ids
    """
    if id_string != "":
        ids = {int(pid) for pid in id_string.split(',')}
    else:
        ids = set()
    return ids


def converter(gila, project_ids=None, group_ids=None,
              only_issues=False, only_milestones=False,
              combine_all_files="", target_directory_path="."):
    """
    central function of the program

    if config_path is None:
        print("There is no path given that leads to your config", file=sys.stderr)
        sys.exit(404)
    """

    path = Path(target_directory_path)
    os.makedirs(path, exist_ok=True)
    print("1 ", path)
    if not path.exists():
        print("There is no valid target directory path", file=sys.stderr)
        sys.exit(202)

    if project_ids is None and group_ids is None:
        print("There are no ids given", file=sys.stderr)
        sys.exit(303)

    # get issues and milestones from either projects or groups
    groups = {}
    projects = {}

    if project_ids:
        for project_id in project_ids:
            project = get_project(gila, project_id)
            issue_events = get_events(project.issues, {"state": "opened"})
            milestone_events = get_events(project.milestones, {"state": "active"})
            events = [issue_events, milestone_events]
            projects[project.name] = events
    if group_ids:
        for group_id in group_ids:
            group = get_group(gila, group_id)
            issue_events = get_events(group.issues, {"state": "opened"})
            milestone_events = get_events(group.milestones, {"state": "active"})
            events = [issue_events, milestone_events]
            groups[group.name] = events
    for e in projects:
        print(projects[e])
    for e in groups:
        print(groups[e])

        # combined cal or many cals
    """
        if combine_all_files and combine_all_files != "False":
            all_events = [set(), set()]
            for group in groups:
                for project in projects:
                    all_events[0] = groups[group][0].union(projects[project][0])
                    all_events[1] = groups[group][1].union(projects[project][1])
            cal = fill_cal_object(all_events, only_issues, only_milestones, create_calendar())
            write_calendar(cal, path.joinpath(combine_all_files), combine_all_files)
        """
    if combine_all_files and combine_all_files != "False":
        all_events = [set(), set()]
        for group in groups:
            print("1")
            print(groups)
            all_events[0].update(groups[group][0])
            all_events[1].update(groups[group][1])
        for project in projects:
            all_events[0].update(projects[project][0])
            all_events[1].update(projects[project][1])
        print(all_events)
        cal = fill_cal_object(all_events, only_issues, only_milestones, create_calendar())
        write_calendar(cal, path.joinpath(combine_all_files), combine_all_files)

    else:
        calendars = []
        for project in projects:
            cal = fill_cal_object(projects[project], only_issues, only_milestones, create_calendar())
            calendars.append((cal, project))
        for group in groups:
            cal = fill_cal_object(groups[group], only_issues, only_milestones, create_calendar())
            calendars.append((cal, group))
        write_calendars(calendars, path)
        """
        # decision, from which project or group the data is going to be taken and put in the calendar-file
        if project_ids:
            for project_id in project_ids:
                project = get_project(gila, project_id)
                cal = fill_cal_object(project, only_issues, only_milestones, create_calendar())
                calendars.append((cal, project.name))
        if group_ids:
            for group_id in group_ids:
                group = get_group(gila, group_id)
                cal = fill_cal_object(group, only_issues, only_milestones, create_calendar())
                calendars.append((cal, group.name))
        write_calendars(calendars, path)
"""


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config",
                        default="../gitlab-config.ini",
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
    parser.add_argument("-com", "--combine",
                        help="If you want to combine all files into one file,"
                             " you should append this to your command and"
                             "the wanted name of your file",
                        type=str)
    args = parser.parse_args()
    if args.config:
        try:
            config = configparser.ConfigParser()
            config.read(args.config)
            args.url = config.get('dlr', 'URL')
            args.token = config.get('dlr', 'PRIVATE_TOKEN')
            args.group = convert_ids(config.get('horen4gim', 'GITLAB_GROUP_ID'))
            args.project = convert_ids(config.get('horen4gim', 'GITLAB_PROJECT_ID'))
            args.issues = bool(config.get('horen4gim', 'ISSUES'))
            args.milestones = bool(config.get('horen4gim', 'MILESTONES'))
            args.combine = config.get('horen4gim', 'COMBINED_FILE')
            args.directory = config.get('horen4gim', 'ABS_PATH')
        except configparser.NoSectionError as e:
            print("Config Missing", e)
        except configparser.NoOptionError as e:
            print("Option Missing", e)

    if not args.url:
        print("There is no url given", file=sys.stderr)
        sys.exit(101)
    if not args.token:
        print("There is no token given", file=sys.stderr)
        sys.exit(505)
    if not args.project and not args.group:
        print("There is no project or group id given", file=sys.stderr)
        sys.exit(606)

    gl = connect_to_gitlab(args.url, args.token)
    converter(gl, args.project, args.group, args.issues, args.milestones, args.combine, args.directory)
