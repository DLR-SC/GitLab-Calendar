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


def get_events_2(project, todos):
    events = set()
    for todo in todos.list(all=True):
        if todo.state == "opened" or todo.state == "active":
            if todo.due_date is not None:
                event = create_event(todo, project.name)
                events.add(event)
    return events


def get_events(project):
    events = set()
    for issue in project.issues.list(all=True, state="opened"):
        if issue.due_date is not None:
            event = create_event(issue, project.name)
            events.add(event)
    for milestone in project.milestones.list(all=True, state="active"):
        event = create_event(milestone, project.name)
        events.add(event)
    return events


def create_event(todo, name):
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

    with open(file_name, 'w', encoding='utf-8') as file:
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


def converter(config_path):
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
    ids = [int(pid) for pid in gitlab_project_id.split(',')]
    path = config.get('horen4gim', 'PATH')
    os.makedirs(path, exist_ok=True)
    calendars = []

    # decision, from which project the data is going to be taken and put in the calendar-file
    if ids:
        for project_id in ids:
            project = get_project(gila, project_id)

            cal = create_calendar()
            # cal.events.update(get_events(project))  (for first get_events function)

            cal.events.update(get_events_2(project, project.issues))
            cal.events.update(get_events_2(project, project.milestones))

            calendars.append((cal, path + project.name))

    else:
        print("No project or group selected")
        sys.exit(1)
    write_calendars(calendars)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", default=None, help="the path of your configuration", type=str)
    # parser.add_argument("-p", "--project", default=[], help="A list of IDs from Projects that you want", type=list)
    # parser.add_argument("-p", "--project",  nargs='+', type=int)
    args = parser.parse_args()
    converter(args.config)
