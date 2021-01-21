
import gitlab
from settings import GITLAB_URL, GITLAB_ACCESS_TOKEN, GITLAB_PROJECT_ID
from ics import Calendar, Event

# def get_project():
# def get_issues_from_project():
# def get_issues_from_group():

# def create_event():


def write_calendar():
    with open('events/' + project.name + '.ics', 'w') as my_file:
        my_file.writelines(c)
    print("Successful creation of the file named \"", project.name, ".ics\".")


if __name__ == "__main__":
    gl = gitlab.Gitlab(GITLAB_URL, GITLAB_ACCESS_TOKEN, ssl_verify=True)
    gl.auth()
    projects = gl.projects.list()
    project = gl.projects.get(GITLAB_PROJECT_ID)
    issues = project.issues.list(all=True, state='opened')
    c = Calendar()
    counter = 0

    for issue in issues:
        issue = project.issues.get(issue.iid)
        if issue.due_date is not None:
            e = Event()
            e.name = 'ID: ' + str(issue.iid) + issue.title
            e.begin = issue.due_date
            e.description = issue.description
            e.location = issue.web_url
            e.make_all_day()
            c.events.add(e)
            print(" TITLE: ", issue.title, "\tDUE_DATE: ", issue.due_date)  # , "\tDESCRIPTION: ", issue.description)
            counter += 1
        else:
            continue

    if counter != 0:
        write_calendar()
    else:
        print("There are no opened issues with a due date in the project.")
