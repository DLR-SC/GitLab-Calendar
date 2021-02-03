"""
Extension for GitLab, that generates ics-files from a repositories issues,
 milestones and iterations, which have a due date.
"""

import os
import configparser
import sys
import argparse
import gitlab
from gitlab.v4.objects import ProjectIssue, ProjectMilestone
from ics import Calendar, Event


def connect_to_gitlab():
    """
    personal access token authentication
    """
    gila = gitlab.Gitlab.from_config("dlr", config_files="../gitlab-config.ini")
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


def get_events(name, api_endpoints, filters):
    events = set()
    for item in api_endpoints.list(all=True, **filters):
        if item.due_date is not None:
            event = create_event(item, name)
            events.add(event)
    return events


def create_event(todo, name="Default Argument"):
    """
    creates a new event and adds it to the calendar object
    """
    event = Event()
    event.name = '[Project:' + name + '] ' + todo.title + ' (' + str(todo.iid) + ')'

    # decision whether the todos are milestones or a issues
    if isinstance(todo, ProjectIssue):
        event.begin = todo.due_date
        event.categories.add("Issues")
        if todo.milestone is None:
            event.description = todo.description
        else:
            event.description = "From Milestone: " + todo.milestone.get("title") + "\n\n" + todo.description
    elif isinstance(todo, ProjectMilestone):
        event.begin = todo.start_date
        event.end = todo.due_date
        event.categories.add("Milestones")
        event.description = todo.description
    event.location = todo.web_url
    event.make_all_day()
    print(" TITLE: ", todo.title, "\tDUE_DATE: ", todo.due_date)
    return event


def write_calendar(calendar, file_name):
    """
    writes a calendar-file from a given calendar object
    """

    with open("events/" + file_name, 'w', encoding='utf-8') as file:
        file.writelines(calendar)
    print("Successful creation of the file named \"" + file_name + "\".")


def write_calendars(calendars):
    """
    calls the "write_calendar" function for each given project
    """
    for calendar, name in calendars:
        write_calendar(calendar, name + '.ics')


def create_calendar():
    """
    creates the calendar object
    """
    cal = Calendar()
    return cal


def write_combined_cal(combined_cal):
    """
    writes a combined file with all the events
    """
    with open('events/combined.ics', 'w') as combined_file:
        combined_file.writelines(combined_cal)
        print("All calendars successfully combined.")


def converter(config_path, ids_from_terminal=""):
    """
    central function of the program
    """
    if config_path is None:
        print("There is no path given that leads to your config", file=sys.stderr)
        sys.exit(404)
    gila = connect_to_gitlab()
    config = configparser.ConfigParser()
    config.read(config_path)
    gitlab_project_id = config.get('horen4gim', 'GITLAB_PROJECT_ID')
    ids = {int(pid) for pid in gitlab_project_id.split(',')}
    if ids_from_terminal:
        terminal_ids = {int(pid) for pid in ids_from_terminal.split(',')}
        ids.update(terminal_ids)
    path = config.get('horen4gim', 'PATH')
    os.makedirs(path, exist_ok=True)
    calendars = []

    # decision, from which project the data is going to be taken and put in the calendar-file
    if ids:
        for project_id in ids:
            project = get_project(gila, project_id)

            cal = create_calendar()
            cal.events.update(get_events(project.name, project.issues, {"state": "opened"}))
            cal.events.update(get_events(project.name, project.milestones, {"state": "active"}))
            calendars.append((cal, project.name))

    else:
        print("No project or group selected")
        sys.exit(1)
    write_calendars(calendars)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", default="../gitlab-config.ini", help="path of your config", type=str)
    parser.add_argument("-p", "--project", default=None,
                        help="All the IDs from Projects that you want, separated by \",\"", type=str)
    args = parser.parse_args()
    converter(args.config, args.project)
