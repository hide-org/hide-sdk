from unittest.mock import create_autospec

import pytest

from hide import Client
from hide.model import File, FileInfo, Line, Project, Repository, Task, TaskResult
from hide.toolkit.toolkit import Toolkit

PROJECT_ID = "123"
PATH = "file.txt"
CONTENT = "Hello World"
PATCH = "test-patch"


@pytest.fixture
def hide_client():
    return create_autospec(Client)


@pytest.fixture
def toolkit(hide_client: Client) -> Toolkit:
    repository = Repository(url="http://example.com/repo.git")
    project = Project(id=PROJECT_ID, repository=repository)
    return Toolkit(project=project, client=hide_client)


def test_get_tasks_success(toolkit: Toolkit, hide_client: Client):
    hide_client.get_tasks.return_value = [Task(alias="build", command="make build")]
    tasks = toolkit.get_tasks()
    assert tasks == '[{"alias": "build", "command": "make build"}]'


def test_get_tasks_failure(toolkit: Toolkit, hide_client: Client):
    hide_client.get_tasks.side_effect = Exception("Error")
    tasks = toolkit.get_tasks()
    assert tasks == "Failed to get tasks: Error"


def test_run_task_command_success(toolkit: Toolkit, hide_client: Client):
    hide_client.run_task.return_value = TaskResult(
        stdout="output", stderr="", exit_code=0
    )
    result = toolkit.run_task(command="echo Hello")
    assert result == "exit code: 0\nstdout: output\nstderr: "


def test_run_task_alias_success(toolkit: Toolkit, hide_client: Client):
    hide_client.run_task.return_value = TaskResult(
        stdout="output", stderr="", exit_code=0
    )
    result = toolkit.run_task(alias="build")
    assert result == "exit code: 0\nstdout: output\nstderr: "


def test_run_task_failure(toolkit: Toolkit, hide_client: Client):
    hide_client.run_task.side_effect = Exception("Error")
    result = toolkit.run_task(command="echo Hello")
    assert result == "Failed to run task: Error"


def test_create_file_success(toolkit: Toolkit, hide_client: Client):
    expected = File(path=PATH, lines=[Line(number=1, content=CONTENT)])
    hide_client.create_file.return_value = expected
    file = toolkit.create_file(PATH, CONTENT)
    assert file == f"File created:\n{expected}"


def test_create_file_failure(toolkit: Toolkit, hide_client: Client):
    hide_client.create_file.side_effect = Exception("Error")
    file = toolkit.create_file(PATH, CONTENT)
    assert file == "Failed to create file: Error"


def test_apply_patch_success(toolkit: Toolkit, hide_client: Client):
    expected = File(path=PATH, lines=[Line(number=1, content=CONTENT)])
    hide_client.update_file.return_value = expected
    file = toolkit.apply_patch(PATH, PATCH)
    assert file == f"File updated:\n{expected}"


def test_apply_patch_failure(toolkit: Toolkit, hide_client: Client):
    hide_client.update_file.side_effect = Exception("Error")
    file = toolkit.apply_patch(PATH, PATCH)
    assert file == "Failed to apply patch: Error"


def test_insert_lines_success(toolkit: Toolkit, hide_client: Client):
    hide_client.get_file.return_value = File(
        path=PATH, lines=[Line(number=1, content=CONTENT)]
    )
    expected = File(
        path=PATH,
        lines=[Line(number=1, content="New line"), Line(number=2, content=CONTENT)],
    )
    hide_client.update_file.return_value = expected
    file = toolkit.insert_lines(PATH, 1, "New line")
    assert file == f"File updated:\n{expected}"


def test_insert_lines_failure(toolkit: Toolkit, hide_client: Client):
    hide_client.get_file.side_effect = Exception("Error")
    file = toolkit.insert_lines(PATH, 1, "New line")
    assert file == "Failed to insert lines: Error"


def test_replace_lines_success(toolkit: Toolkit, hide_client: Client):
    hide_client.get_file.return_value = File(
        path=PATH,
        lines=[Line(number=1, content=CONTENT), Line(number=2, content="Old line")],
    )
    expected = File(
        path=PATH,
        lines=[Line(number=1, content=CONTENT), Line(number=2, content="New line")],
    )
    hide_client.update_file.return_value = expected
    file = toolkit.replace_lines(PATH, 2, 3, "New line")
    assert file == f"File updated:\n{expected}"


def test_replace_lines_failure(toolkit: Toolkit, hide_client: Client):
    hide_client.get_file.side_effect = Exception("Error")
    file = toolkit.replace_lines(PATH, 1, 2, "New line")
    assert file == "Failed to replace lines: Error"


def test_append_lines_success(toolkit: Toolkit, hide_client: Client):
    hide_client.get_file.return_value = File(
        path=PATH, lines=[Line(number=1, content=CONTENT)]
    )
    expected = File(
        path=PATH,
        lines=[Line(number=1, content=CONTENT), Line(number=2, content="New line")],
    )
    hide_client.update_file.return_value = expected
    file = toolkit.append_lines(PATH, "New line")
    assert file == f"File updated:\n{expected}"


def test_append_lines_failure(toolkit: Toolkit, hide_client: Client):
    hide_client.get_file.side_effect = Exception("Error")
    file = toolkit.append_lines(PATH, "New line")
    assert file == "Failed to append lines: Error"


def test_get_file_success(toolkit: Toolkit, hide_client: Client):
    expected = File(path=PATH, lines=[Line(number=1, content=CONTENT)])
    hide_client.get_file.return_value = expected
    file = toolkit.get_file(PATH)
    assert file == f"{expected}"


def test_get_file_failure(toolkit: Toolkit, hide_client: Client):
    hide_client.get_file.side_effect = Exception("Error")
    file = toolkit.get_file(PATH)
    assert file == "Failed to get file: Error"


def test_delete_file_success(toolkit: Toolkit, hide_client: Client):
    hide_client.delete_file.return_value = True
    file = toolkit.delete_file(PATH)
    assert file == f"File deleted: {PATH}"


def test_delete_file_failure(toolkit: Toolkit, hide_client: Client):
    hide_client.delete_file.side_effect = Exception("Error")
    file = toolkit.delete_file(PATH)
    assert file == "Failed to delete file: Error"


def test_list_files_success(toolkit: Toolkit, hide_client: Client):
    hide_client.list_files.return_value = [FileInfo(path="README.md")]
    files = toolkit.list_files()
    assert files == "README.md"


def test_list_files_failure(toolkit: Toolkit, hide_client: Client):
    hide_client.list_files.side_effect = Exception("Error")
    files = toolkit.list_files()
    assert files == "Failed to list files: Error"
