import asyncio
from langchain_core.pydantic_v1 import BaseModel, Field

from langchain_community.agent_toolkits.base import BaseToolkit
from langchain_core.tools import BaseTool, tool

from hide.client.hide_client import HideClient, HideClientSync
from hide.client.models.exec_cmd_request import ExecCmdRequest

class ExecCmdRequestModel(BaseModel):
    cmd: str = Field(..., description="The command to run.")

class ExecCmdResultModel(BaseModel):
    stdOut: str = Field(..., description="The standard output of the command.")
    stdErr: str = Field(..., description="The standard error of the command.")
    exitCode: int = Field(..., description="The exit code of the command.")


class HideToolkit(BaseToolkit):
    project_id: str = Field(..., description="The project ID to run the command in.")
    hide_client: HideClientSync = Field(..., description="The Hide client to use.")

    class Config:
        arbitrary_types_allowed = True

    def exec_cmd(self, cmd: str) -> ExecCmdResultModel:
        return ExecCmdResultModel.parse_obj(
            self.hide_client.exec_cmd(project_id=self.project_id, cmd=cmd)
        )

    def get_tools(self) -> list[BaseTool]:
        """Get the tools in the toolkit."""

        @tool(args_schema=ExecCmdRequestModel)
        def exec_cmd(cmd: str) -> str:
            """Execute a command in the shell."""
            return self.exec_cmd(cmd).stdOut

        return [exec_cmd]
