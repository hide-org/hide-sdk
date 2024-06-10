import asyncio
import json
from typing import Optional
from langchain_core.pydantic_v1 import BaseModel, Field

from langchain_community.agent_toolkits.base import BaseToolkit
from langchain_core.tools import BaseTool, tool

from hide.client.hide_client import HideClient

class RunTaskArgs(BaseModel):
    command: Optional[str] = Field(default=None, description="The command to run.")
    alias: Optional[str] = Field(default=None, description="The alias of the task to run.")

class FileArgs(BaseModel):
    path: str = Field(..., description="The path of the file.")
    content: str = Field(..., description="The content of the file.")


class HideToolkit(BaseToolkit):
    project_id: str = Field(..., description="The project ID to run the command in.")
    hide_client: HideClient = Field(..., description="The Hide client to use.")

    class Config:
        arbitrary_types_allowed = True

    def get_tools(self) -> list[BaseTool]:
        """Get the tools in the toolkit."""

        @tool()
        def get_tasks() -> str:
            """Get the tasks in the project."""
            try:
                tasks = self.hide_client.get_tasks(self.project_id)
                return json.dumps([task.model_dump() for task in tasks])
            except Exception as e:
                return f"Failed to get tasks: {e}"

        @tool(args_schema=RunTaskArgs)
        def run_task(command: Optional[str] = None, alias: Optional[str] = None) -> str:
            """
            Run a task in the project. Provide either command or alias. Command will be executed in the shell. 
            For the list of available tasks, use the `get_tasks` tool.
            """
            try:
                result = self.hide_client.run_task(project_id=self.project_id, command=command, alias=alias)
                return f"exit code: {result.exitCode}\nstdout: {result.stdOut}\nstderr: {result.stdErr}"
            except Exception as e:
                return f"Failed to run task: {e}"

        @tool(args_schema=FileArgs)
        def create_file(path: str, content: str) -> str:
            """Create a file in the project."""
            try:
                file = self.hide_client.create_file(project_id=self.project_id, path=path, content=content)
                return f"File created: {file.path}"
            except Exception as e:
                return f"Failed to create file: {e}"

        @tool(args_schema=FileArgs)
        def update_file(path: str, content: str) -> str:
            """Update a file in the project."""
            try:
                file = self.hide_client.update_file(project_id=self.project_id, path=path, content=content)
                return f"File updated: {file.path}"
            except Exception as e:
                return f"Failed to update file: {e}"

        @tool()
        def get_file(path: str) -> str:
            """Get a file from the project."""
            try:
                file = self.hide_client.get_file(project_id=self.project_id, path=path)
                return f"```{file.path}\n{file.content}```"
            except Exception as e:
                return f"Failed to get file: {e}"

        @tool()
        def delete_file(path: str) -> str:
            """Delete a file from the project."""
            try:
                deleted = self.hide_client.delete_file(project_id=self.project_id, path=path)
                return f"File deleted: {path}" if deleted else f"Failed to delete file: {path}"
            except Exception as e:
                return f"Failed to delete file: {e}"

        @tool()
        def list_files() -> str:
            """List files in the project."""
            try:
                files = self.hide_client.list_files(project_id=self.project_id)
                return "\n".join([file.path for file in files])
            except Exception as e:
                return f"Failed to list files: {e}"

        return [get_tasks, run_task, create_file, update_file, get_file, delete_file, list_files]
