
import gitlab
from settings import GITLAB_URL, GITLAB_ACCESS_TOKEN, GITLAB_PROJECT_ID
from ics import Calendar, Event


def connect_to_gitlab():
    gila = gitlab.Gitlab(GITLAB_URL, GITLAB_ACCESS_TOKEN, ssl_verify=True)
    gila.auth()
    return gila


def get_project():
    proj = gl.projects.get(GITLAB_PROJECT_ID)
    return proj


def get_issues_from_project():
    counter = 0
    for issue in issues:
        issue = project.issues.get(issue.iid)
        if issue.due_date is not None:
            create_event(issue)
            counter += 1
        else:
            continue
    return counter

# def get_issues_from_group():


def create_event(issue):
    e = Event()
    e.name = '[' + project.name + '] ' + issue.title + ' (' + str(issue.iid) + ')'
    e.begin = issue.due_date
    e.description = issue.description
    e.location = issue.web_url
    e.make_all_day()
    cal.events.add(e)
    print(" TITLE: ", issue.title, "\tDUE_DATE: ", issue.due_date)  # , "\tDESCRIPTION: ", issue.description)


def create_calendar():
    c = Calendar()
    return c


def write_calendar():
    if issue_counter != 0:
        with open('events/' + project.name + '.ics', 'w') as my_file:
            my_file.writelines(cal)
        print("Successful creation of the file named \"" + project.name + ".ics\".")
    else:
        print("There are no opened issues with a due date in the project.")


if __name__ == "__main__":
    gl = connect_to_gitlab()
    project = get_project()
    issues = project.issues.list(all=True, state='opened')
    cal = create_calendar()
    issue_counter = get_issues_from_project()
    write_calendar()
