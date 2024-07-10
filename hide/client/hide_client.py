from typing import Optional
from pydantic import BaseModel, Field
import requests

from hide.devcontainer.model import DevContainer


class Repository(BaseModel):
    url: str = Field(..., description="The URL of the repository.")
    commit: Optional[str] = Field(
        default=None,
        description="The commit hash to create the project from. If not provided, the latest commit will be used.",
    )


class File(BaseModel):
    path: str = Field(..., description="The path of the file.")
    content: str = Field(..., description="The content of the file.")


class CreateProjectRequest(BaseModel):
    repository: Repository = Field(
        ..., description="The repository to create the project from."
    )
    devcontainer: Optional[DevContainer] = Field(
        default=None,
        description="The dev container configuration to use for the project. If not provided, the configuration from the repository will be used. If the repository does not contain a dev container, the request will fail.",
    )
    files: Optional[list[File]] = Field(
        default=None,
        description="The files to include in the project environment.",
    )


class Project(BaseModel):
    id: str = Field(..., description="The ID of the project.")


class TaskResult(BaseModel):
    stdOut: str = Field(..., description="The standard output of the command.")
    stdErr: str = Field(..., description="The standard error of the command.")
    exitCode: int = Field(..., description="The exit code of the command.")


class Task(BaseModel):
    alias: str = Field(..., description="The alias of the task.")
    command: str = Field(..., description="The shell command to run the task.")


class FileInfo(BaseModel):
    path: str = Field(..., description="The path of the file.")


class HideClient:

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    def create_project(self, request: CreateProjectRequest) -> Project:
        response = requests.post(f"{self.base_url}/projects", json=request.model_dump(exclude_unset=True))
        if not response.ok:
            raise HideClientError(response.text)
        return Project.model_validate(response.json())

    def delete_project(self, project: Project) -> bool:
        response = requests.delete(f"{self.base_url}/projects/{project.id}")
        if not response.ok:
            raise HideClientError(response.text)
        return response.status_code == 204

    def get_tasks(self, project_id: str) -> list[Task]:
        response = requests.get(f"{self.base_url}/projects/{project_id}/tasks")
        if not response.ok:
            raise HideClientError(response.text)
        return [Task.model_validate(task) for task in response.json()]

    def run_task(
        self,
        project_id: str,
        command: Optional[str] = None,
        alias: Optional[str] = None,
    ) -> TaskResult:
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
        return TaskResult.model_validate(response.json())

    def create_file(self, project_id: str, path: str, content: str) -> File:
        response = requests.post(
            f"{self.base_url}/projects/{project_id}/files",
            json={"path": path, "content": content},
        )
        if not response.ok:
            raise HideClientError(response.text)
        return File.model_validate(response.json())

    def get_file(self, project_id: str, path: str) -> File:
        response = requests.get(f"{self.base_url}/projects/{project_id}/files/{path}")
        if not response.ok:
            raise HideClientError(response.text)
        return File.model_validate(response.json())

    def update_file(self, project_id: str, path: str, content: str) -> File:
        print(f"Updating file {path} in project {project_id}")
        print(content)
        response = requests.put(
            f"{self.base_url}/projects/{project_id}/files/{path}",
            json={"content": content},
        )
        if not response.ok:
            raise HideClientError(response.text)
        return File.model_validate(response.json())

    def delete_file(self, project_id: str, path: str) -> bool:
        response = requests.delete(
            f"{self.base_url}/projects/{project_id}/files/{path}"
        )
        if not response.ok:
            raise HideClientError(response.text)
        return response.status_code == 204

    def list_files(self, project_id: str) -> list[FileInfo]:
        response = requests.get(f"{self.base_url}/projects/{project_id}/files")
        if not response.ok:
            raise HideClientError(response.text)
        return [FileInfo.model_validate(file) for file in response.json()]


class HideClientError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
