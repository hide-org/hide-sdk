from unittest.mock import create_autospec

import pytest

from hide.client.hide_client import HideClient, Project
from hide.toolkit.toolkit import Toolkit
from hide.model import File, Line, Task, TaskResult, FileInfo

PROJECT_ID = "123"
PATH = "file.txt"
CONTENT = "Hello World"
PATCH = "test-patch"


@pytest.fixture
def hide_client():
    return create_autospec(HideClient)

@pytest.fixture
def toolkit(hide_client: HideClient) -> Toolkit:
    project = Project(id=PROJECT_ID)
    return Toolkit(project=project, client=hide_client)


def test_get_tasks_success(toolkit: Toolkit, hide_client: HideClient):
    hide_client.get_tasks.return_value = [Task(alias="build", command="make build")]
    tasks = toolkit.get_tasks()
    assert tasks == '[{"alias": "build", "command": "make build"}]'


def test_get_tasks_failure(toolkit: Toolkit, hide_client: HideClient):
    hide_client.get_tasks.side_effect = Exception("Error")
    tasks = toolkit.get_tasks()
    assert tasks == 'Failed to get tasks: Error'


def test_run_task_command_success(toolkit: Toolkit, hide_client: HideClient):
    hide_client.run_task.return_value = TaskResult(stdout="output", stderr="", exit_code=0)
    result = toolkit.run_task(command="echo Hello")
    assert result == 'exit code: 0\nstdout: output\nstderr: '


def test_run_task_alias_success(toolkit: Toolkit, hide_client: HideClient):
    hide_client.run_task.return_value = TaskResult(stdout="output", stderr="", exit_code=0)
    result = toolkit.run_task(alias="build")
    assert result == 'exit code: 0\nstdout: output\nstderr: '


def test_run_task_failure(toolkit: Toolkit, hide_client: HideClient):
    hide_client.run_task.side_effect = Exception("Error")
    result = toolkit.run_task(command="echo Hello")
    assert result == 'Failed to run task: Error'


def test_create_file_success(toolkit: Toolkit, hide_client: HideClient):
    hide_client.create_file.return_value = File(path=PATH, lines=[Line(number=1, content=CONTENT)])
    file = toolkit.create_file(PATH, CONTENT)
    assert file == f'File created: {PATH}\n1 | {CONTENT}\n'


def test_create_file_failure(toolkit: Toolkit, hide_client: HideClient):
    hide_client.create_file.side_effect = Exception("Error")
    file = toolkit.create_file(PATH, CONTENT)
    assert file == 'Failed to create file: Error'


def test_apply_patch_success(toolkit: Toolkit, hide_client: HideClient):
    hide_client.update_file.return_value = File(path=PATH, lines=[Line(number=1, content=CONTENT)])
    file = toolkit.apply_patch(PATH, PATCH)
    assert file == f'File updated: {PATH}\n1 | {CONTENT}\n'


def test_apply_patch_failure(toolkit: Toolkit, hide_client: HideClient):
    hide_client.update_file.side_effect = Exception("Error")
    file = toolkit.apply_patch(PATH, PATCH)
    assert file == 'Failed to apply patch: Error'


def test_insert_lines_success(toolkit: Toolkit, hide_client: HideClient):
    hide_client.get_file.return_value = File(path=PATH, lines=[Line(number=1, content=CONTENT)])
    hide_client.update_file.return_value = File(path=PATH, lines=[Line(number=1, content="New line"), Line(number=2, content=CONTENT)])
    file = toolkit.insert_lines(PATH, 1, "New line")
    assert file == f'File updated: {PATH}\n1 | New line\n2 | {CONTENT}\n'


def test_insert_lines_failure(toolkit: Toolkit, hide_client: HideClient):
    hide_client.get_file.side_effect = Exception("Error")
    file = toolkit.insert_lines(PATH, 1, "New line")
    assert file == 'Failed to insert lines: Error'


def test_replace_lines_success(toolkit: Toolkit, hide_client: HideClient):
    hide_client.get_file.return_value = File(path=PATH, lines=[Line(number=1, content=CONTENT), Line(number=2, content="Old line")])
    hide_client.update_file.return_value = File(path=PATH, lines=[Line(number=1, content=CONTENT), Line(number=2, content="New line")])
    file = toolkit.replace_lines(PATH, 2, 3, "New line")
    assert file == f'File updated: {PATH}\n1 | {CONTENT}\n2 | New line\n'


def test_replace_lines_failure(toolkit: Toolkit, hide_client: HideClient):
    hide_client.get_file.side_effect = Exception("Error")
    file = toolkit.replace_lines(PATH, 1, 2, "New line")
    assert file == 'Failed to replace lines: Error'


def test_append_lines_success(toolkit: Toolkit, hide_client: HideClient):
    hide_client.get_file.return_value = File(path=PATH, lines=[Line(number=1, content=CONTENT)])
    hide_client.update_file.return_value = File(path=PATH, lines=[Line(number=1, content=CONTENT), Line(number=2, content="New line")])
    file = toolkit.append_lines(PATH, "New line")
    assert file == f'File updated: {PATH}\n1 | {CONTENT}\n2 | New line\n'


def test_append_lines_failure(toolkit: Toolkit, hide_client: HideClient):
    hide_client.get_file.side_effect = Exception("Error")
    file = toolkit.append_lines(PATH, "New line")
    assert file == 'Failed to append lines: Error'


def test_get_file_success(toolkit: Toolkit, hide_client: HideClient):
    hide_client.get_file.return_value = File(path=PATH, lines=[Line(number=1, content=CONTENT)])
    file = toolkit.get_file(PATH)
    assert file == f'```{PATH}\n1 | {CONTENT}\n```'


def test_get_file_failure(toolkit: Toolkit, hide_client: HideClient):
    hide_client.get_file.side_effect = Exception("Error")
    file = toolkit.get_file(PATH)
    assert file == 'Failed to get file: Error'


def test_delete_file_success(toolkit: Toolkit, hide_client: HideClient):
    hide_client.delete_file.return_value = True
    file = toolkit.delete_file(PATH)
    assert file == f'File deleted: {PATH}'


def test_delete_file_failure(toolkit: Toolkit, hide_client: HideClient):
    hide_client.delete_file.side_effect = Exception("Error")
    file = toolkit.delete_file(PATH)
    assert file == 'Failed to delete file: Error'


def test_list_files_success(toolkit: Toolkit, hide_client: HideClient):
    hide_client.list_files.return_value = [FileInfo(path="README.md")]
    files = toolkit.list_files()
    assert files == 'README.md'


def test_list_files_failure(toolkit: Toolkit, hide_client: HideClient):
    hide_client.list_files.side_effect = Exception("Error")
    files = toolkit.list_files()
    assert files == 'Failed to list files: Error'
