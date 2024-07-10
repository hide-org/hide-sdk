import pytest
from unittest.mock import patch, Mock
from pydantic import ValidationError
from hide.client.hide_client import (
    FileInfo,
    HideClient,
    CreateProjectRequest,
    Project,
    Repository,
    Task,
    TaskResult,
    File,
    HideClientError,
)


@pytest.fixture
def client():
    return HideClient(base_url="http://localhost")


def test_create_project_success(client):
    request_data = CreateProjectRequest(repository=Repository(url="http://example.com/repo.git"))
    response_data = {"id": "123"}
    with patch("requests.post") as mock_post:
        mock_post.return_value = Mock(ok=True, json=lambda: response_data)
        project = client.create_project(request_data)
        assert project == Project(id="123")
        mock_post.assert_called_once_with(
            "http://localhost/projects", json=request_data.model_dump()
        )


def test_create_project_failure(client):
    request_data = CreateProjectRequest(repository=Repository(url="http://example.com/repo.git"))
    with patch("requests.post") as mock_post:
        mock_post.return_value = Mock(ok=False, text="Error")
        with pytest.raises(HideClientError, match="Error"):
            client.create_project(request_data)


def test_get_tasks_success(client):
    project_id = "123"
    response_data = [{"alias": "build", "command": "make build"}]
    with patch("requests.get") as mock_get:
        mock_get.return_value = Mock(ok=True, json=lambda: response_data)
        tasks = client.get_tasks(project_id)
        assert len(tasks) == 1
        assert tasks[0] == Task(alias="build", command="make build")
        mock_get.assert_called_once_with("http://localhost/projects/123/tasks")


def test_get_tasks_failure(client):
    project_id = "123"
    with patch("requests.get") as mock_get:
        mock_get.return_value = Mock(ok=False, text="Error")
        with pytest.raises(HideClientError, match="Error"):
            client.get_tasks(project_id)


def test_run_task_command_success(client):
    project_id = "123"
    response_data = {"stdOut": "output", "stdErr": "", "exitCode": 0}
    with patch("requests.post") as mock_post:
        mock_post.return_value = Mock(ok=True, json=lambda: response_data)
        result = client.run_task(project_id, command="echo Hello")
        assert result == TaskResult(stdOut="output", stdErr="", exitCode=0)
        mock_post.assert_called_once_with(
            "http://localhost/projects/123/tasks", json={"command": "echo Hello"}
        )


def test_run_task_alias_success(client):
    project_id = "123"
    response_data = {"stdOut": "output", "stdErr": "", "exitCode": 0}
    with patch("requests.post") as mock_post:
        mock_post.return_value = Mock(ok=True, json=lambda: response_data)
        result = client.run_task(project_id, alias="build")
        assert result == TaskResult(stdOut="output", stdErr="", exitCode=0)
        mock_post.assert_called_once_with(
            "http://localhost/projects/123/tasks", json={"alias": "build"}
        )


def test_run_task_failure(client):
    project_id = "123"
    with patch("requests.post") as mock_post:
        mock_post.return_value = Mock(ok=False, text="Error")
        with pytest.raises(HideClientError, match="Error"):
            client.run_task(project_id, command="echo Hello")


def test_run_task_no_command_or_alias(client):
    project_id = "123"
    with pytest.raises(
        HideClientError, match="Either 'command' or 'alias' must be provided"
    ):
        client.run_task(project_id)


def test_run_task_command_and_alias(client):
    project_id = "123"
    with pytest.raises(
        HideClientError, match="Cannot provide both 'command' and 'alias'"
    ):
        client.run_task(project_id, command="echo Hello", alias="build")


def test_create_file_success(client):
    project_id = "123"
    path = "README.md"
    content = "Hello World"
    response_data = {"path": path, "content": content}
    with patch("requests.post") as mock_post:
        mock_post.return_value = Mock(ok=True, json=lambda: response_data)
        file = client.create_file(project_id, path, content)
        assert file == File(path=path, content=content)
        mock_post.assert_called_once_with(
            "http://localhost/projects/123/files",
            json={"path": path, "content": content},
        )


def test_create_file_failure(client):
    project_id = "123"
    path = "README.md"
    content = "Hello World"
    with patch("requests.post") as mock_post:
        mock_post.return_value = Mock(ok=False, text="Error")
        with pytest.raises(HideClientError, match="Error"):
            client.create_file(project_id, path, content)


def test_get_file_success(client):
    project_id = "123"
    path = "README.md"
    response_data = {"path": path, "content": "Hello World"}
    with patch("requests.get") as mock_get:
        mock_get.return_value = Mock(ok=True, json=lambda: response_data)
        file = client.get_file(project_id, path)
        assert file == File(path=path, content="Hello World")
        mock_get.assert_called_once_with(f"http://localhost/projects/123/files/{path}")


def test_get_file_failure(client):
    project_id = "123"
    path = "README.md"
    with patch("requests.get") as mock_get:
        mock_get.return_value = Mock(ok=False, text="Error")
        with pytest.raises(HideClientError, match="Error"):
            client.get_file(project_id, path)


def test_update_file_success(client):
    project_id = "123"
    path = "README.md"
    content = "Updated Content"
    with patch("requests.put") as mock_put:
        mock_put.return_value = Mock(
            ok=True, json=lambda: {"path": path, "content": content}
        )
        file = client.update_file(project_id, path, content)
        assert file == File(path=path, content=content)
        mock_put.assert_called_once_with(
            f"http://localhost/projects/123/files/{path}", json={"content": content}
        )


def test_update_file_failure(client):
    project_id = "123"
    path = "README.md"
    content = "Updated Content"
    with patch("requests.put") as mock_put:
        mock_put.return_value = Mock(ok=False, text="Error")
        with pytest.raises(HideClientError, match="Error"):
            client.update_file(project_id, path, content)


def test_delete_file_success(client):
    project_id = "123"
    path = "README.md"
    with patch("requests.delete") as mock_delete:
        mock_delete.return_value = Mock(ok=True, status_code=204)
        assert client.delete_file(project_id, path)
        mock_delete.assert_called_once_with(
            f"http://localhost/projects/123/files/{path}"
        )


def test_delete_file_failure(client):
    project_id = "123"
    path = "README.md"
    with patch("requests.delete") as mock_delete:
        mock_delete.return_value = Mock(ok=False, text="Error")
        with pytest.raises(HideClientError, match="Error"):
            client.delete_file(project_id, path)


def test_list_files_success(client):
    project_id = "123"
    response_data = [{"path": "README.md", "content": "Hello World"}]
    with patch("requests.get") as mock_get:
        mock_get.return_value = Mock(ok=True, json=lambda: response_data)
        files = client.list_files(project_id)
        assert files == [FileInfo(path="README.md")]


def test_list_files_failure(client):
    project_id = "123"
    with patch("requests.get") as mock_get:
        mock_get.return_value = Mock(ok=False, text="Error")
        with pytest.raises(HideClientError, match="Error"):
            client.list_files(project_id)
