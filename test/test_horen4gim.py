from datetime import datetime

import gitlab
import pytest
from ics import Calendar, Event
from pathlib import Path
# from gitlab.v4.objects import Project, Group
from horen4gim import merge_events, create_event, write_calendar, write_calendars, filter_events

gl = gitlab.Gitlab.from_config("dlr", config_files="gitlab-config.ini")
e1 = Event(name="e1", location="url1", begin=datetime(2021, 1, 27, 11, 30))
e2 = Event(name="e2", location="url2", begin=datetime(2021, 1, 27, 11, 30))
e3 = Event(name="e3", location="url3", begin=datetime(2021, 1, 27, 11, 30))
e4 = Event(name="e4", location="url4", begin=datetime(2021, 1, 27, 11, 30))
e5 = Event(name="e5same_as_e4", location="url4", begin=datetime(2021, 1, 27, 11, 30))
cal1 = Calendar(events={e1, e2})
cal2 = Calendar(events={e3, e4})
cal3 = Calendar()
calendars = [(cal1, "cal1"), (cal2, "cal2"), (cal3, "cal3")]


@pytest.mark.parametrize("groups,projects,expected_events", [
    ({"g1": {e1, e2}}, {"p1": {e4}}, {e1, e2, e4}),
    ({}, {"p1": {e1, e2, e3}}, {e1, e2, e3}),
    ({"g1": {e1, e2, e3}}, {"p1": {}}, {e1, e2, e3}),
    ({"g1": {e1}}, {"p1": {e3, e4}, "p2": {e2}}, {e1, e2, e3, e4}),
    ({"g1": {e1, e2, e4}}, {"p1": {e4}}, {e1, e2, e4}),
    ])
def test_merge_events_success(groups, projects, expected_events):
    # with pytest.raises(Exception):
    result_events = merge_events(groups, projects)
    assert result_events == expected_events


@pytest.mark.parametrize("groups,projects,expected_events", [
    ({"g1": {e1, e2, e4}}, {"p1": {e5}}, {e1, e2, e4}),
    ])
def test_merge_events_double_event_url(groups, projects, expected_events):
    """
    problem with same urls at different events
    """
    result_events = merge_events(groups, projects)
    assert result_events == expected_events


@pytest.mark.parametrize("project_id,issue_id", [
    (10064, 11),
    (10064, 10),

    ])
def test_create_event(project_id, issue_id):

    project = gl.projects.get(project_id)
    issue = project.issues.get(issue_id)
    if issue.due_date:
        event = create_event(issue, project)
        assert project.name in event.name
        assert event.categories == {"Issues"}
        assert issue.description in event.description


def test_write_calendar(tmpdir):
    cal = Calendar()
    date = datetime(2021, 1, 27, 11, 30)
    event = Event(name='testevent',
                  begin=date)
    filename = str(tmpdir + 'test.ics')
    cal.events.add(event)
    write_calendar(cal, filename, "test.ics")
    with open(filename, 'r') as f:
        content = f.readlines()
    assert 'testevent' in ''.join(content)


@pytest.mark.parametrize("cals", [
    calendars
])
def test_write_calendars(tmpdir, cals):
    p = tmpdir.mkdir("test")
    write_calendars(calendars, Path(p))
    with open(str(p + "/cal1.ics"), 'r') as f:
        content = f.readlines()
    assert 'e1' in ''.join(content)
    assert 'LOCATION:url1' in ''.join(content)
    assert Path(str(p + "/cal3.ics")).exists() is False


def test_filter_todos_from_project():
    issue_events, milestone_events = filter_events(gl.projects.get(10064),
                                                   True, True)
    assert issue_events != set()
    assert milestone_events != set()
