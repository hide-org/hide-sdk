from typing import Optional

from langchain_community.agent_toolkits.base import BaseToolkit
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool, tool

from hide.toolkit import Toolkit


class RunTaskArgs(BaseModel):
    command: Optional[str] = Field(default=None, description="The command to run.")
    alias: Optional[str] = Field(
        default=None, description="The alias of the task to run."
    )


class FileArgs(BaseModel):
    path: str = Field(..., description="The path of the file.")
    content: str = Field(..., description="The content of the file.")


class LangchainToolkit(BaseToolkit):
    toolkit: Toolkit = Field(..., description="The Hide toolkit to use.")

    class Config:
        arbitrary_types_allowed = True

    def get_tools(self) -> list[BaseTool]:
        """Get the Langchain-compatible tools."""
        return list(map(lambda _tool: tool(_tool), self.toolkit.get_tools()))
