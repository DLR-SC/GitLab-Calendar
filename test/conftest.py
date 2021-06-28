# SPDX-FileCopyrightText: 2021 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

from unittest import mock
import pytest

from gitlab.v4.objects import Project, Group
from gitlab.v4.objects import ProjectManager, GroupManager, IssueManager, GroupMilestoneManager, ProjectMilestoneManager
from gitlab.v4.objects import ProjectIssue, ProjectMilestone, GroupIssue, GroupMilestone


@pytest.fixture
def api():
    projects = mock.Mock(spec=ProjectManager, get=mock.Mock())
    groups = mock.Mock(spec=GroupManager, get=mock.Mock())
    issues = mock.Mock(spec=IssueManager,list=mock.Mock())
    return mock.Mock(projects=projects, groups=groups, issues=issues)
