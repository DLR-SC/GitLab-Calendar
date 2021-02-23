# SPDX-FileCopyrightText: 2021 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

from unittest import mock
import pytest


@pytest.fixture
def _project(status, _id, ref):
    pipeline_list = [mock.Mock(status=status, id=_id, ref=ref)]
    pipelines = mock.Mock(list=mock.Mock(return_value=pipeline_list))
    branches = mock.Mock(list=mock.Mock(return_value=pipeline_list))
    branches.name = ref
    _project = mock.Mock(pipelines=pipelines, branches=branches)
    _project.name = "Test"
    return _project

@pytest.fixture
def group():
    projects_list = [mock.Mock(status="false", id=9873, ref="master")]
    projects = mock.Mock(list=mock.Mock(return_value=projects_list))
    group = mock.Mock(projects=projects)
    return group

@pytest.fixture
def gl(_project,group):
    groups=mock.Mock(list=mock.Mock(return_value=[mock.Mock(return_value=group),mock.Mock(return_value=group)]),get=mock.Mock(return_value=group))
    projects = mock.Mock(get=mock.Mock(return_value=_project))
    return mock.Mock(projects=projects, groups = groups)
