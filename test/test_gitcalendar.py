# SPDX-FileCopyrightText: 2021 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

from datetime import datetime
from unittest import mock
from pathlib import Path

import pytest
from ics import Calendar, Event
from gitlab.v4.objects import Project, Group
from gitlab.v4.objects import ProjectManager, GroupManager, IssueManager, GroupMilestoneManager, ProjectMilestoneManager
from gitlab.v4.objects import ProjectIssue, ProjectMilestone, GroupIssue, GroupMilestone

from gitcalendar.gitcalendar import (
    merge_events, create_event, filter_events,
    write_calendar, write_calendars, convert_ids
)

p1 = mock.Mock(spec=Project, id=1337)

i1 = mock.Mock(spec=ProjectIssue, title="I1", due_date=datetime(2021, 1, 27, 11, 30), web_url="https://example.org/i1")
i2 = mock.Mock(spec=ProjectIssue, title="I2", due_date=datetime(2021, 1, 27, 11, 30), web_url="https://example.org/i2")
i3 = mock.Mock(spec=ProjectIssue, title="I3", due_date=datetime(2021, 1, 27, 11, 30), web_url="https://example.org/i3")
i4 = mock.Mock(spec=ProjectIssue, title="I4", due_date=datetime(2021, 1, 27, 11, 30), web_url="https://example.org/i4")

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


@pytest.mark.skip("Needs mocking")
@pytest.mark.parametrize("issue, project, expected_event", [
    (i1, p1, e1),
    (i2, p1, e2)
])
def test_create_event(api, issue, project, expected_event):
    project.name = "TestProject"
    event = create_event(api, issue, project, 0.0)
    assert project.name in event.name


def test_write_calendar(tmpdir):
    cal = Calendar()
    date = datetime(2021, 1, 27, 11, 30)
    event = Event(name='test_event', begin=date)
    filename = str(tmpdir + 'test.ics')
    cal.events.add(event)
    write_calendar(cal, filename, "test.ics")
    with open(filename, 'r') as f:
        content = f.readlines()
    assert 'test_event' in ''.join(content)


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


@pytest.mark.skip("Needs mocking")
def test_filter_todos_from_project(api):
    issue_events, milestone_events = filter_events(api, api.projects.get(10064),
                                                   only_issues=True, only_milestones=True, reminder=0.0)
    assert issue_events != set()
    assert milestone_events != set()


@pytest.mark.parametrize("id_string,expected", [
    ("10064,10074,hello", {10064, 10074}),
    ("1331,34424,31a2", {1331, 34424}),
    ("invalid;23,42", {42})
])
def test_convert_ids_success(id_string, expected):
    ids = convert_ids(id_string)
    assert ids == expected


def test_convert_empty_ids():
    ids = convert_ids("")
    assert ids is None
