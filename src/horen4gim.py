
import gitlab
import configparser
from ics import Calendar, Event


def connect_to_gitlab():
    """
    personal access token authentication
    """
    gl = gitlab.Gitlab.from_config("dlr", config_files="../gitlab-config.ini")
    gl.auth()
    return gl


def get_project(gl, project_id):
    """
    returns a specific project from a given ID
    """
    instance = gl.projects.get(project_id)
    return instance


def get_group(gl, group_id):
    """
    returns a specific group from a given ID
    """
    instance = gl.groups.get(group_id)
    return instance


def get_events_from_issues(project):
    """
    gets the terminated issues from a project and creates events with them
    """
    events = set()
    for issue in project.issues.list(all=True, state='opened'):
        if issue.due_date is not None:
            event = create_event(issue, project.name)
            events.add(event)

    return events


def create_event(issue, name):
    """
    creates a new event and adds it to the calendar object
    """
    e = Event()
    e.name = '[' + name + '] ' + issue.title + ' (' + str(issue.iid) + ')'
    e.begin = issue.due_date
    e.description = issue.description
    e.location = issue.web_url
    e.make_all_day()
    print(" TITLE: ", issue.title, "\tDUE_DATE: ", issue.due_date)
    return e


def write_calendar(calendar, file_name):
    with open(file_name, 'w') as f:
        f.writelines(calendar)
    print("Successful creation of the file named \"" + file_name + ".ics\".")


def write_calendars(calendars):
    for calendar, name in calendars:
        write_calendar(calendar, name + '.ics')
    pass


def create_calendar():
    """
    creates the calendar object
    """
    c = Calendar()
    return c


def write_combined_cal(combined_cal):
    """
    writes a combined file with all the events
    """
    with open('events/combined.ics', 'w') as combined_file:
        combined_file.writelines(combined_cal)
        print("All calendars successfully combined.")


def menu():

    gl = connect_to_gitlab()
    config = configparser.ConfigParser()
    config.read('../gitlab-config.ini')
    gitlab_project_id = config.get('horen4gim', 'GITLAB_PROJECT_ID')
    ids = [int(pid) for pid in gitlab_project_id.split(',')]
    path = config.get('horen4gim', 'PATH')
    calendars = []

    # decision, from which project or group the data is going to be taken and put in the calendar-file
    if ids:
        for project_id in ids:
            project = get_project(gl, project_id)
            cal = create_calendar()
            issue_events = get_events_from_issues(project)
            cal.events.update(issue_events)
            calendars.append((cal, path + project.name))

    else:
        print("No project or group selected")
        exit(1)
    write_calendars(calendars)


if __name__ == "__main__":
    menu()
