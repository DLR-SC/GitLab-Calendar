from datetime import datetime

import gitlab
import pytest
from ics import Calendar, Event
from gitlab.v4.objects import Project, Group
from horen4gim import merge_events, create_event
# from horen4gim import create_calendar, write_calendar, create_event, get_events, get_instance


e1 = Event(name="e1", location="url1")
e2 = Event(name="e2", location="url2")
e3 = Event(name="e3", location="url3")
e4 = Event(name="e4", location="url4")
e5 = Event(name="e5same_as_e4", location="url4")


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
    gl = gitlab.Gitlab.from_config("dlr", config_files="gitlab-config.ini")
    project = gl.projects.get(project_id)
    issue = project.issues.get(issue_id)
    if issue.due_date:
        event = create_event(issue, project)
        assert project.name in event.name
        assert event.categories == {"Issues"}
        assert issue.description in event.description

# def test_create_calendar():
#     cal = create_calendar()
#     assert cal.creator is None
#     assert cal.events == set()
#
#
# def test_get_instance():
#     instance_id1 = 5224
#     instance_id2 = 10064
#     instance1 = get_instance(gl, instance_id1)
#     instance2 = get_instance(gl, instance_id2)
#     assert type(instance1) is Project
#     assert type(instance2) is Project
#
#
# def test_write_calendar(tmpdir):
#     cal = Calendar()
#     date = datetime(2021, 1, 27, 11, 30)
#     event = Event(name='testevent',
#                   begin=date)
#     filename = str(tmpdir + 'test.ics')
#     cal.events.add(event)
#     write_calendar(cal, filename)
#     with open(filename, 'r') as f:
#         content = f.readlines()
#     assert 'testevent' in ''.join(content)
#
#
# def test_get_events():
#     instance = gl.projects.get(10064)
#     events = get_events(instance.name, instance.issues, {"state": "opened"})
#     assert type(events) == set
#     assert events != ()
#
#
# def test_create_event():
#     project = gl.projects.get(10064)
#     for issue in project.issues.list(all=True, state='opened'):
#         if issue.due_date is not None:
#             event = create_event(issue, project.name)
#             assert event.location == issue.web_url
#             assert event.description == issue.description
