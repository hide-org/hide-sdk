from typing import Any, Optional, Union

import requests

from hide import model
from hide.devcontainer.model import DevContainer

DEFAULT_BASE_URL = "http://localhost:8080"


class HideClient:
    def __init__(self, base_url: str = DEFAULT_BASE_URL) -> None:
        self.base_url = base_url

    def create_project(
        self,
        repository: model.Repository,
        devcontainer: Optional[DevContainer] = None,
        languages: Optional[list[model.Language]] = None,
    ) -> model.Project:
        request = model.CreateProjectRequest(
            repository=repository, devcontainer=devcontainer, languages=languages
        )
        response = requests.post(
            f"{self.base_url}/projects",
            json=request.model_dump(exclude_unset=True, exclude_none=True),
        )
        if not response.ok:
            raise HideClientError(response.text)
        return model.Project.model_validate(response.json())

    def delete_project(self, project: model.Project) -> bool:
        response = requests.delete(f"{self.base_url}/projects/{project.id}")
        if not response.ok:
            raise HideClientError(response.text)
        return response.status_code == 204

    def get_tasks(self, project_id: str) -> list[model.Task]:
        response = requests.get(f"{self.base_url}/projects/{project_id}/tasks")
        if not response.ok:
            raise HideClientError(response.text)
        return [model.Task.model_validate(task) for task in response.json()]

    def run_task(
        self,
        project_id: str,
        command: Optional[str] = None,
        alias: Optional[str] = None,
    ) -> model.TaskResult:
        if not command and not alias:
            raise HideClientError("Either 'command' or 'alias' must be provided")

        if command and alias:
            raise HideClientError("Cannot provide both 'command' and 'alias'")

        payload = {}
        if command:
            payload["command"] = command
        if alias:
            payload["alias"] = alias

        response = requests.post(
            f"{self.base_url}/projects/{project_id}/tasks", json=payload
        )
        if not response.ok:
            raise HideClientError(response.text)
        return model.TaskResult.model_validate(response.json())

    def create_file(
        self, project_id: str, path: model.FilePath, content: str
    ) -> model.File:
        response = requests.post(
            f"{self.base_url}/projects/{project_id}/files",
            json={"path": path, "content": content},
        )
        if not response.ok:
            raise HideClientError(response.text)
        return model.File.model_validate(response.json())

    def get_file(
        self,
        project_id: str,
        path: model.FilePath,
        start_line: Optional[int] = None,
        num_lines: Optional[int] = None,
    ) -> model.File:
        response = requests.get(
            url=f"{self.base_url}/projects/{project_id}/files/{path}",
            params={"startLine": start_line, "numLines": num_lines},
        )
        if not response.ok:
            raise HideClientError(response.text)
        return model.File.model_validate(response.json())

    def update_file(
        self,
        project_id: str,
        path: model.FilePath,
        update: Union[model.UdiffUpdate, model.LineDiffUpdate, model.OverwriteUpdate],
    ) -> model.File:
        match update:
            case model.UdiffUpdate() as udiff:
                payload = {
                    "type": model.FileUpdateType.UDIFF.value,
                    "udiff": udiff.model_dump(by_alias=True),
                }
            case model.LineDiffUpdate() as linediff:
                payload = {
                    "type": model.FileUpdateType.LINEDIFF.value,
                    "linediff": linediff.model_dump(by_alias=True),
                }
            case model.OverwriteUpdate() as overwrite:
                payload = {
                    "type": model.FileUpdateType.OVERWRITE.value,
                    "overwrite": overwrite.model_dump(by_alias=True),
                }
            case _:
                raise ValueError(f"Invalid file update type: {type}")

        response = requests.put(
            f"{self.base_url}/projects/{project_id}/files/{path}",
            json=payload,
        )
        if not response.ok:
            raise HideClientError(response.text)
        return model.File.model_validate(response.json())

    def delete_file(
        self, project_id: str, file: model.FilePath | model.File | model.FileInfo
    ) -> bool:
        if isinstance(file, model.FileInfo):
            file = file.path

        if isinstance(file, model.File):
            file = file.path

        response = requests.delete(
            f"{self.base_url}/projects/{project_id}/files/{file}"
        )
        if not response.ok:
            raise HideClientError(response.text)
        return response.status_code == 204

    def list_files(
        self,
        project_id: str,
        include: Optional[list[str]] = None,
        exclude: Optional[list[str]] = None,
    ) -> list[model.FileInfo]:
        params: dict[str, Any] = {}
        if include:
            params["include"] = include
        if exclude:
            params["exclude"] = exclude

        response = requests.get(
            url=f"{self.base_url}/projects/{project_id}/files", params=params
        )
        if not response.ok:
            raise HideClientError(response.text)
        return [model.FileInfo.model_validate(file) for file in response.json()]

    def search_files(
        self,
        project_id: str,
        query: str,
        search_mode: model.SearchMode = model.SearchMode.DEFAULT,
        show_hidden: bool = False,
        include: Optional[list[str]] = None,
        exclude: Optional[list[str]] = None,
    ) -> list[model.File]:
        params: dict[str, Any] = {"query": query, "type": "content"}

        if search_mode == model.SearchMode.EXACT:
            params["exact"] = ""
        if search_mode == model.SearchMode.REGEX:
            params["regex"] = ""
        if show_hidden:
            params["showHidden"] = ""
        if include:
            params["include"] = include
        if exclude:
            params["exclude"] = exclude

        response = requests.get(
            f"{self.base_url}/projects/{project_id}/search", params=params
        )

        if not response.ok:
            raise HideClientError(response.text)
        return [model.File.model_validate(file) for file in response.json()]

    def search_symbols(
        self,
        project_id: str,
        query: str,
        limit: Optional[int] = None,
    ) -> list[model.Symbol]:
        params: dict[str, Any] = {"query": query}

        if limit:
            params["limit"] = limit

        response = requests.get(
            f"{self.base_url}/projects/{project_id}/search?type=symbol", params=params
        )

        if not response.ok:
            raise HideClientError(response.text)
        return [model.Symbol.model_validate(symbol) for symbol in response.json()]


class HideClientError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
