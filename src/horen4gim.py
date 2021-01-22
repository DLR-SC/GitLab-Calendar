
import gitlab
from settings import GITLAB_URL, GITLAB_ACCESS_TOKEN, GITLAB_PROJECT_ID, GITLAB_GROUP_ID
from ics import Calendar, Event


def connect_to_gitlab():               # personal access token authentication
    gila = gitlab.Gitlab(GITLAB_URL, GITLAB_ACCESS_TOKEN, ssl_verify=True)
    gila.auth()
    return gila


def get_project():                      # returns a specific project from a given ID
    proj = gl.projects.get(GITLAB_PROJECT_ID)
    return proj


def get_group():                        # returns a specific group from a given ID
    gr = gl.groups.get(GITLAB_GROUP_ID)
    return gr


def get_issues_from_project():          # gets the terminated issues from a project and creates events with them
    counter = 0
    name = project.name
    for issue in issues:
        issue = project.issues.get(issue.iid)
        if issue.due_date is not None:
            create_event(issue, name)
            counter += 1
        else:
            continue
    return counter


def get_issues_from_group():                # gets the terminated issues from a group and creates events with them
    counter = 0
    name = group.name
    for issue in group.issues.list():
        if issue.due_date is not None:
            create_event(issue, name)
            counter += 1
        else:
            continue
    return counter


def create_event(issue, name):                 # creates a new event and adds it to the calendar object
    e = Event()
    e.name = '[' + name + '] ' + issue.title + ' (' + str(issue.iid) + ')'
    e.begin = issue.due_date
    e.description = issue.description
    e.location = issue.web_url
    e.make_all_day()
    cal.events.add(e)
    print(" TITLE: ", issue.title, "\tDUE_DATE: ", issue.due_date)


def create_calendar():              # creates the calendar object
    c = Calendar()
    return c


def write_calendar_file(file_name):          # writes all events into a calendar file
    if issue_counter != 0:
        with open('events/' + file_name + '.ics', 'w') as my_file:
            my_file.writelines(cal)
        print("Successful creation of the file named \"" + file_name + ".ics\".")
    else:
        print("There are no opened issues with a due date in the project.")


if __name__ == "__main__":
    gl = connect_to_gitlab()

    # decision, from which project or group the data is going to be taken and put in the calendar-file
    if GITLAB_PROJECT_ID or GITLAB_GROUP_ID is not None:
        if GITLAB_PROJECT_ID is not None:
            project = get_project()
            issues = project.issues.list(all=True, state='opened')
            cal = create_calendar()
            issue_counter = get_issues_from_project()
            write_calendar_file(project.name)
        if GITLAB_GROUP_ID is not None:
            group = get_group()
            issues = group.issues.list(all=True, state='opened')
            cal = create_calendar()
            issue_counter = get_issues_from_group()
            write_calendar_file(group.name)
    else:
        print("No project or group selected")
