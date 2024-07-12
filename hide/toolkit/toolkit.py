import json
from typing import Callable, Optional

from hide.client.hide_client import HideClient, Project


class Toolkit:
    def __init__(self, project: Project, client: HideClient) -> None:
        self.project = project
        self.client = client

    def get_tools(self) -> list[Callable[..., str]]:
        def get_tasks() -> str:
            """Get the tasks in the project."""
            try:
                tasks = self.client.get_tasks(self.project.id)
                return json.dumps([task.model_dump() for task in tasks])
            except Exception as e:
                return f"Failed to get tasks: {e}"

        def run_task(command: Optional[str] = None, alias: Optional[str] = None) -> str:
            """
            Run a task in the project. Provide either command or alias. Command will be executed in the shell.
            For the list of available tasks, use the `get_tasks` tool.
            """
            try:
                result = self.client.run_task(
                    project_id=self.project.id, command=command, alias=alias
                )
                return f"exit code: {result.exitCode}\nstdout: {result.stdOut}\nstderr: {result.stdErr}"
            except Exception as e:
                return f"Failed to run task: {e}"

        def create_file(path: str, content: str) -> str:
            """Create a file in the project."""
            try:
                file = self.client.create_file(
                    project_id=self.project.id, path=path, content=content
                )
                return f"File created: {file.path}"
            except Exception as e:
                return f"Failed to create file: {e}"

        def update_file(path: str, content: str) -> str:
            """Update a file in the project."""
            try:
                file = self.client.update_file(
                    project_id=self.project.id, path=path, content=content
                )
                return f"File updated: {file.path}"
            except Exception as e:
                return f"Failed to update file: {e}"

        def get_file(path: str) -> str:
            """Get a file from the project."""
            try:
                file = self.client.get_file(project_id=self.project.id, path=path)
                return f"```{file.path}\n{file.content}```"
            except Exception as e:
                return f"Failed to get file: {e}"

        def delete_file(path: str) -> str:
            """Delete a file from the project."""
            try:
                deleted = self.client.delete_file(project_id=self.project.id, path=path)
                return (
                    f"File deleted: {path}"
                    if deleted
                    else f"Failed to delete file: {path}"
                )
            except Exception as e:
                return f"Failed to delete file: {e}"

        def list_files() -> str:
            """List files in the project."""
            try:
                files = self.client.list_files(project_id=self.project.id)
                return "\n".join([file.path for file in files])
            except Exception as e:
                return f"Failed to list files: {e}"

        return [
            get_tasks,
            run_task,
            create_file,
            update_file,
            get_file,
            delete_file,
            list_files,
        ]

    def as_langchain(self) -> "LangchainToolkit":
        from hide.langchain.toolkit import LangchainToolkit

        return LangchainToolkit(toolkit=self)
