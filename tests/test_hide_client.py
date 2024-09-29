from unittest.mock import Mock, patch

import pytest

import hide
from hide import model
from hide.client import HideClientError

PROJECT_ID = "123"
PATH = "file.txt"
CONTENT = "Hello World"
FILE = {"path": PATH, "lines": [{"number": 1, "content": CONTENT}]}


@pytest.fixture
def client() -> hide.Client:
    return hide.Client(base_url="http://localhost")


def test_create_project_success(client: hide.Client):
    repository = model.Repository(url="http://example.com/repo.git")
    request_data = model.CreateProjectRequest(repository=repository)
    response_data = {"id": "123"}

    with patch("requests.post") as mock_post:
        mock_post.return_value = Mock(ok=True, json=lambda: response_data)
        project = client.create_project(repository=repository)
        assert project == model.Project(id="123")
        mock_post.assert_called_once_with(
            "http://localhost/projects",
            json=request_data.model_dump(exclude_unset=True),
        )


def test_create_project_failure(client: hide.Client):
    repository = model.Repository(url="http://example.com/repo.git")

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
        assert tasks[0] == model.Task(alias="build", command="make build")
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
        assert result == model.TaskResult(stdout="output", stderr="", exit_code=0)
        mock_post.assert_called_once_with(
            "http://localhost/projects/123/tasks", json={"command": "echo Hello"}
        )


def test_run_task_alias_success(client):
    response_data = {"stdout": "output", "stderr": "", "exitCode": 0}
    with patch("requests.post") as mock_post:
        mock_post.return_value = Mock(ok=True, json=lambda: response_data)
        result = client.run_task(PROJECT_ID, alias="build")
        assert result == model.TaskResult(stdout="output", stderr="", exit_code=0)
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
        assert file == model.File.from_content(path=PATH, content=CONTENT)
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
        assert file == model.File.from_content(path=PATH, content=CONTENT)
        mock_get.assert_called_once_with(
            url=f"http://localhost/projects/123/files/{PATH}",
            params={"startLine": None, "numLines": None},
        )


def test_get_file_with_start_line(client):
    with patch("requests.get") as mock_get:
        mock_get.return_value = Mock(ok=True, json=lambda: FILE)
        file = client.get_file(PROJECT_ID, PATH, start_line=10)
        assert file == model.File.from_content(path=PATH, content="Hello World")
        mock_get.assert_called_once_with(
            url=f"http://localhost/projects/123/files/{PATH}",
            params={"startLine": 10, "numLines": None},
        )


def test_get_file_with_num_lines(client):
    with patch("requests.get") as mock_get:
        mock_get.return_value = Mock(ok=True, json=lambda: FILE)
        file = client.get_file(PROJECT_ID, PATH, num_lines=10)
        assert file == model.File.from_content(path=PATH, content="Hello World")
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
        file = client.update_file(
            PROJECT_ID, PATH, model.UdiffUpdate(patch="test-patch")
        )
        assert file == model.File.from_content(path=PATH, content=CONTENT)
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
            model.LineDiffUpdate(start_line=1, end_line=10, content="test-content"),
        )
        assert file == model.File.from_content(path=PATH, content=CONTENT)
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
        file = client.update_file(
            PROJECT_ID, PATH, model.OverwriteUpdate(content=CONTENT)
        )
        assert file == model.File.from_content(path=PATH, content=CONTENT)
        mock_put.assert_called_once_with(
            f"http://localhost/projects/123/files/{PATH}",
            json={"type": "overwrite", "overwrite": {"content": CONTENT}},
        )


def test_update_file_failure(client):
    with patch("requests.put") as mock_put:
        mock_put.return_value = Mock(ok=False, text="Error")
        with pytest.raises(HideClientError, match="Error"):
            client.update_file(PROJECT_ID, PATH, model.UdiffUpdate(patch="test-patch"))


def test_delete_file_success(client):
    with patch("requests.delete") as mock_delete:
        mock_delete.return_value = Mock(ok=True, status_code=204)
        assert client.delete_file(PROJECT_ID, PATH)
        mock_delete.assert_called_once_with(
            f"http://localhost/projects/123/files/{PATH}"
        )


def test_delete_file_with_file(client):
    with patch("requests.delete") as mock_delete:
        mock_delete.return_value = Mock(ok=True, status_code=204)
        assert client.delete_file(PROJECT_ID, model.File(path=PATH))
        mock_delete.assert_called_once_with(
            f"http://localhost/projects/123/files/{PATH}"
        )


def test_delete_file_with_file_info(client):
    with patch("requests.delete") as mock_delete:
        mock_delete.return_value = Mock(ok=True, status_code=204)
        assert client.delete_file(PROJECT_ID, model.FileInfo(path=PATH))
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
        assert files == [model.FileInfo(path="README.md")]
        mock_get.assert_called_once_with(
            url="http://localhost/projects/123/files", params={}
        )


def test_list_files_with_include_param(client):
    response_data = [{"path": "src/main.py", "content": "print('Hello')"}]
    with patch("requests.get") as mock_get:
        mock_get.return_value = Mock(ok=True, json=lambda: response_data)
        files = client.list_files(PROJECT_ID, include=["src/**/*.py"])
        assert files == [model.FileInfo(path="src/main.py")]
        mock_get.assert_called_once_with(
            url="http://localhost/projects/123/files",
            params={"include": ["src/**/*.py"]},
        )


def test_list_files_with_exclude_param(client):
    response_data = [{"path": "README.md", "content": "# Project"}]
    with patch("requests.get") as mock_get:
        mock_get.return_value = Mock(ok=True, json=lambda: response_data)
        files = client.list_files(PROJECT_ID, exclude=["*.py", "*.js"])
        assert files == [model.FileInfo(path="README.md")]
        mock_get.assert_called_once_with(
            url="http://localhost/projects/123/files",
            params={"exclude": ["*.py", "*.js"]},
        )


def test_list_files_with_include_and_exclude_params(client):
    response_data = [{"path": "src/util.py", "content": "# Utility functions"}]
    with patch("requests.get") as mock_get:
        mock_get.return_value = Mock(ok=True, json=lambda: response_data)
        files = client.list_files(
            PROJECT_ID, include=["src/**/*.py"], exclude=["src/test_*.py"]
        )
        assert files == [model.FileInfo(path="src/util.py")]
        mock_get.assert_called_once_with(
            url="http://localhost/projects/123/files",
            params={"include": ["src/**/*.py"], "exclude": ["src/test_*.py"]},
        )


def test_list_files_failure(client):
    with patch("requests.get") as mock_get:
        mock_get.return_value = Mock(ok=False, text="Error")
        with pytest.raises(HideClientError, match="Error"):
            client.list_files(PROJECT_ID)


def test_search_files_default(client):
    response_data = [
        {"path": "src/main.py", "lines": [{"number": 1, "content": "Hello"}]}
    ]
    with patch("requests.get") as mock_get:
        mock_get.return_value = Mock(ok=True, json=lambda: response_data)
        files = client.search_files(PROJECT_ID, query="Hello")
        assert files == [model.File.from_content(path="src/main.py", content="Hello")]
        mock_get.assert_called_once_with(
            f"http://localhost/projects/{PROJECT_ID}/search",
            params={"query": "Hello", "type": "content"},
        )


def test_search_files_exact(client):
    response_data = [
        {
            "path": "src/util.py",
            "lines": [{"number": 1, "content": "def hello(): pass"}],
        }
    ]
    with patch("requests.get") as mock_get:
        mock_get.return_value = Mock(ok=True, json=lambda: response_data)
        files = client.search_files(
            PROJECT_ID,
            query="hello",
            search_mode=model.SearchMode.EXACT,
        )
        assert files == [
            model.File.from_content(path="src/util.py", content="def hello(): pass")
        ]
        mock_get.assert_called_once_with(
            f"http://localhost/projects/{PROJECT_ID}/search",
            params={
                "query": "hello",
                "type": "content",
                "exact": "",
            },
        )


def test_search_files_regex(client):
    response_data = [
        {
            "path": "src/util.py",
            "lines": [{"number": 1, "content": "def hello(): pass"}],
        }
    ]
    with patch("requests.get") as mock_get:
        mock_get.return_value = Mock(ok=True, json=lambda: response_data)
        files = client.search_files(
            PROJECT_ID,
            query="hello",
            search_mode=model.SearchMode.REGEX,
        )
        assert files == [
            model.File.from_content(path="src/util.py", content="def hello(): pass")
        ]
        mock_get.assert_called_once_with(
            f"http://localhost/projects/{PROJECT_ID}/search",
            params={
                "query": "hello",
                "type": "content",
                "regex": "",
            },
        )


def test_search_files_hidden(client):
    response_data = [
        {
            "path": "src/util.py",
            "lines": [{"number": 1, "content": "def hello(): pass"}],
        }
    ]
    with patch("requests.get") as mock_get:
        mock_get.return_value = Mock(ok=True, json=lambda: response_data)
        files = client.search_files(
            PROJECT_ID,
            query="hello",
            show_hidden=True,
        )
        assert files == [
            model.File.from_content(path="src/util.py", content="def hello(): pass")
        ]
        mock_get.assert_called_once_with(
            f"http://localhost/projects/{PROJECT_ID}/search",
            params={
                "query": "hello",
                "type": "content",
                "showHidden": "",
            },
        )


def test_search_files_with_include(client):
    response_data = [
        {
            "path": "src/util.py",
            "lines": [{"number": 1, "content": "def hello(): pass"}],
        }
    ]
    with patch("requests.get") as mock_get:
        mock_get.return_value = Mock(ok=True, json=lambda: response_data)
        files = client.search_files(
            PROJECT_ID,
            query="hello",
            include=["src/**/*.py"],
        )
        assert files == [
            model.File.from_content(path="src/util.py", content="def hello(): pass")
        ]
        mock_get.assert_called_once_with(
            f"http://localhost/projects/{PROJECT_ID}/search",
            params={
                "query": "hello",
                "type": "content",
                "include": ["src/**/*.py"],
            },
        )


def test_search_files_with_exclude(client):
    response_data = [
        {
            "path": "src/util.py",
            "lines": [{"number": 1, "content": "def hello(): pass"}],
        }
    ]
    with patch("requests.get") as mock_get:
        mock_get.return_value = Mock(ok=True, json=lambda: response_data)
        files = client.search_files(
            PROJECT_ID,
            query="hello",
            exclude=["src/**/*.py"],
        )
        assert files == [
            model.File.from_content(path="src/util.py", content="def hello(): pass")
        ]
        mock_get.assert_called_once_with(
            f"http://localhost/projects/{PROJECT_ID}/search",
            params={
                "query": "hello",
                "type": "content",
                "exclude": ["src/**/*.py"],
            },
        )


def test_search_files_failure(client):
    with patch("requests.get") as mock_get:
        mock_get.return_value = Mock(ok=False, text="Error")
        with pytest.raises(HideClientError, match="Error"):
            client.search_files(PROJECT_ID, query="test")
