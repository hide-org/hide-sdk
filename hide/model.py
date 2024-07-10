from typing import Optional

from pydantic import BaseModel, Field

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
