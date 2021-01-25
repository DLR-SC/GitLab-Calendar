
import gitlab
from settings import GITLAB_URL, GITLAB_ACCESS_TOKEN, GITLAB_PROJECT_ID, GITLAB_GROUP_ID
from ics import Calendar, Event


def connect_to_gitlab(url, token):
    """
    personal access token authentication
    """
    gl = gitlab.Gitlab(url, token, ssl_verify=True)
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


def get_issues_from_instance(combined_cal, c, instance, name):
    """
    gets the terminated issues from a project or group and creates events with them
    """
    counter = 0
    for issue in instance.issues.list(all=True, state='opened'):
        if issue.due_date is not None:
            create_event(combined_cal, c, issue, name)
            counter += 1
    return counter, name


def create_event(combined_cal, c, issue, name):
    """
    creates a new event and adds it to the calendar object
    """
    e = Event()
    e.name = '[' + name + '] ' + issue.title + ' (' + str(issue.iid) + ')'
    e.begin = issue.due_date
    e.description = issue.description
    e.location = issue.web_url
    e.make_all_day()
    c.events.add(e)
    combined_cal.events.add(e)
    print(" TITLE: ", issue.title, "\tDUE_DATE: ", issue.due_date)


def fill_calendar(combined_cal, instance):
    """
    fills the calendar through given issues from a specific project or group
    """
    cal = create_calendar()
    issue_counter, file_name = get_issues_from_instance(combined_cal, cal, instance, instance.name)
    write_calendar_file(issue_counter, file_name, cal)


def create_calendar():
    """
    creates the calendar object
    """
    c = Calendar()
    return c


def write_calendar_file(issue_counter, name, cal):
    """
    writes all events into a calendar file
    """
    if issue_counter != 0:
        with open('events/' + name + '.ics', 'w') as my_file:
            my_file.writelines(cal)
        print("Successful creation of the file named \"" + name + ".ics\".")

    else:
        print("There are no opened issues with a due date in the project.")


def write_combined_cal(combined_cal):
    """
    writes a combined file with all the events
    """
    with open('events/combined.ics', 'w') as combined_file:
        combined_file.writelines(combined_cal)
        print("All calendars successfully combined.")


def menu():
    gl = connect_to_gitlab(GITLAB_URL, GITLAB_ACCESS_TOKEN)

    # decision, from which project or group the data is going to be taken and put in the calendar-file
    if GITLAB_PROJECT_ID or GITLAB_GROUP_ID != []:
        combined_cal = create_calendar()
        if GITLAB_PROJECT_ID:
            for project_id in GITLAB_PROJECT_ID:
                instance = get_project(gl, project_id)
                fill_calendar(combined_cal, instance)
        if GITLAB_GROUP_ID:
            for group_id in GITLAB_GROUP_ID:
                instance = get_group(gl, group_id)
                fill_calendar(combined_cal, instance)
        write_combined_cal(combined_cal)
    else:
        print("No project or group selected")


if __name__ == "__main__":
    menu()
