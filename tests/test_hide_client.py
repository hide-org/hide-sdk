from unittest.mock import Mock, patch

import pytest

from hide.client.hide_client import (
    CreateProjectRequest,
    File,
    FileInfo,
    HideClient,
    HideClientError,
    Project,
    Repository,
    Task,
    TaskResult,
)
from hide.model import LineDiffUpdate, OverwriteUpdate, UdiffUpdate

PROJECT_ID = "123"
PATH = "file.txt"
CONTENT = "Hello World"
FILE = {"path": PATH, "lines": [{"number": 1, "content": CONTENT}]}


@pytest.fixture
def client() -> HideClient:
    return HideClient(base_url="http://localhost")


def test_create_project_success(client: HideClient):
    repository = Repository(url="http://example.com/repo.git")
    request_data = CreateProjectRequest(repository=repository)
    response_data = {"id": "123"}

    with patch("requests.post") as mock_post:
        mock_post.return_value = Mock(ok=True, json=lambda: response_data)
        project = client.create_project(repository=repository)
        assert project == Project(id="123")
        mock_post.assert_called_once_with(
            "http://localhost/projects",
            json=request_data.model_dump(exclude_unset=True),
        )


def test_create_project_failure(client: HideClient):
    repository = Repository(url="http://example.com/repo.git")

    with patch("requests.post") as mock_post:
        mock_post.return_value = Mock(ok=False, text="Error")
        with pytest.raises(HideClientError, match="Error"):
            client.create_project(repository=repository)


def test_get_tasks_success(client):
    response_data = [{"alias": "build", "command": "make build"}]
    with patch("requests.get") as mock_get:
        mock_get.return_value = Mock(ok=True, json=lambda: response_data)
        tasks = client.get_tasks(PROJECT_ID)
        assert len(tasks) == 1
        assert tasks[0] == Task(alias="build", command="make build")
        mock_get.assert_called_once_with("http://localhost/projects/123/tasks")


def test_get_tasks_failure(client):
    with patch("requests.get") as mock_get:
        mock_get.return_value = Mock(ok=False, text="Error")
        with pytest.raises(HideClientError, match="Error"):
            client.get_tasks(PROJECT_ID)


def test_run_task_command_success(client):
    response_data = {"stdout": "output", "stderr": "", "exitCode": 0}
    with patch("requests.post") as mock_post:
        mock_post.return_value = Mock(ok=True, json=lambda: response_data)
        result = client.run_task(PROJECT_ID, command="echo Hello")
        assert result == TaskResult(stdout="output", stderr="", exit_code=0)
        mock_post.assert_called_once_with(
            "http://localhost/projects/123/tasks", json={"command": "echo Hello"}
        )


def test_run_task_alias_success(client):
    response_data = {"stdout": "output", "stderr": "", "exitCode": 0}
    with patch("requests.post") as mock_post:
        mock_post.return_value = Mock(ok=True, json=lambda: response_data)
        result = client.run_task(PROJECT_ID, alias="build")
        assert result == TaskResult(stdout="output", stderr="", exit_code=0)
        mock_post.assert_called_once_with(
            "http://localhost/projects/123/tasks", json={"alias": "build"}
        )


def test_run_task_failure(client):
    with patch("requests.post") as mock_post:
        mock_post.return_value = Mock(ok=False, text="Error")
        with pytest.raises(HideClientError, match="Error"):
            client.run_task(PROJECT_ID, command="echo Hello")


def test_run_task_no_command_or_alias(client):
    with pytest.raises(
        HideClientError, match="Either 'command' or 'alias' must be provided"
    ):
        client.run_task(PROJECT_ID)


def test_run_task_command_and_alias(client):
    with pytest.raises(
        HideClientError, match="Cannot provide both 'command' and 'alias'"
    ):
        client.run_task(PROJECT_ID, command="echo Hello", alias="build")


def test_create_file_success(client):
    with patch("requests.post") as mock_post:
        mock_post.return_value = Mock(ok=True, json=lambda: FILE)
        file = client.create_file(PROJECT_ID, PATH, CONTENT)
        assert file == File.from_content(path=PATH, content=CONTENT)
        mock_post.assert_called_once_with(
            "http://localhost/projects/123/files",
            json={"path": PATH, "content": CONTENT},
        )


def test_create_file_failure(client):
    with patch("requests.post") as mock_post:
        mock_post.return_value = Mock(ok=False, text="Error")
        with pytest.raises(HideClientError, match="Error"):
            client.create_file(PROJECT_ID, PATH, CONTENT)


def test_get_file(client):
    with patch("requests.get") as mock_get:
        mock_get.return_value = Mock(ok=True, json=lambda: FILE)
        file = client.get_file(PROJECT_ID, PATH)
        assert file == File.from_content(path=PATH, content=CONTENT)
        mock_get.assert_called_once_with(
            url=f"http://localhost/projects/123/files/{PATH}",
            params={"startLine": None, "numLines": None},
        )


def test_get_file_with_start_line(client):
    with patch("requests.get") as mock_get:
        mock_get.return_value = Mock(ok=True, json=lambda: FILE)
        file = client.get_file(PROJECT_ID, PATH, start_line=10)
        assert file == File.from_content(path=PATH, content="Hello World")
        mock_get.assert_called_once_with(
            url=f"http://localhost/projects/123/files/{PATH}",
            params={"startLine": 10, "numLines": None},
        )


def test_get_file_with_num_lines(client):
    with patch("requests.get") as mock_get:
        mock_get.return_value = Mock(ok=True, json=lambda: FILE)
        file = client.get_file(PROJECT_ID, PATH, num_lines=10)
        assert file == File.from_content(path=PATH, content="Hello World")
        mock_get.assert_called_once_with(
            url=f"http://localhost/projects/123/files/{PATH}",
            params={"startLine": None, "numLines": 10},
        )


def test_get_file_failure(client):
    with patch("requests.get") as mock_get:
        mock_get.return_value = Mock(ok=False, text="Error")
        with pytest.raises(HideClientError, match="Error"):
            client.get_file(PROJECT_ID, PATH)


def test_update_file_with_udiff_succeeds(client):
    with patch("requests.put") as mock_put:
        mock_put.return_value = Mock(ok=True, json=lambda: FILE)
        file = client.update_file(PROJECT_ID, PATH, UdiffUpdate(patch="test-patch"))
        assert file == File.from_content(path=PATH, content=CONTENT)
        mock_put.assert_called_once_with(
            f"http://localhost/projects/123/files/{PATH}",
            json={"type": "udiff", "udiff": {"patch": "test-patch"}},
        )


def test_update_file_with_linediff_succeeds(client):
    with patch("requests.put") as mock_put:
        mock_put.return_value = Mock(ok=True, json=lambda: FILE)
        file = client.update_file(
            PROJECT_ID,
            PATH,
            LineDiffUpdate(start_line=1, end_line=10, content="test-content"),
        )
        assert file == File.from_content(path=PATH, content=CONTENT)
        mock_put.assert_called_once_with(
            f"http://localhost/projects/123/files/{PATH}",
            json={
                "type": "linediff",
                "linediff": {"startLine": 1, "endLine": 10, "content": "test-content"},
            },
        )


def test_update_file_with_overwrite_succeeds(client):
    with patch("requests.put") as mock_put:
        mock_put.return_value = Mock(ok=True, json=lambda: FILE)
        file = client.update_file(PROJECT_ID, PATH, OverwriteUpdate(content=CONTENT))
        assert file == File.from_content(path=PATH, content=CONTENT)
        mock_put.assert_called_once_with(
            f"http://localhost/projects/123/files/{PATH}",
            json={"type": "overwrite", "overwrite": {"content": CONTENT}},
        )


def test_update_file_failure(client):
    with patch("requests.put") as mock_put:
        mock_put.return_value = Mock(ok=False, text="Error")
        with pytest.raises(HideClientError, match="Error"):
            client.update_file(PROJECT_ID, PATH, UdiffUpdate(patch="test-patch"))


def test_delete_file_success(client):
    with patch("requests.delete") as mock_delete:
        mock_delete.return_value = Mock(ok=True, status_code=204)
        assert client.delete_file(PROJECT_ID, PATH)
        mock_delete.assert_called_once_with(
            f"http://localhost/projects/123/files/{PATH}"
        )


def test_delete_file_failure(client):
    with patch("requests.delete") as mock_delete:
        mock_delete.return_value = Mock(ok=False, text="Error")
        with pytest.raises(HideClientError, match="Error"):
            client.delete_file(PROJECT_ID, PATH)


def test_list_files_success(client):
    response_data = [{"path": "README.md", "content": "Hello World"}]
    with patch("requests.get") as mock_get:
        mock_get.return_value = Mock(ok=True, json=lambda: response_data)
        files = client.list_files(PROJECT_ID)
        assert files == [FileInfo(path="README.md")]


def test_list_files_failure(client):
    with patch("requests.get") as mock_get:
        mock_get.return_value = Mock(ok=False, text="Error")
        with pytest.raises(HideClientError, match="Error"):
            client.list_files(PROJECT_ID)
