from enum import Enum, IntEnum
from typing import List, Optional, Union

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from hide.devcontainer.model import DevContainer

UpperLeftCorner = "\u250C"
UpperRightCorner = "\u2510"
LowerLeftCorner = "\u2514"
LowerRightCorner = "\u2518"
VerticalLine = "\u2502"
HorizontalLine = "\u2500"
HorizontalEllipsis = "\u2026"

FilePath = str


class Repository(BaseModel):
    url: str = Field(..., description="The URL of the repository.")
    commit: Optional[str] = Field(
        default=None,
        description="The commit hash to create the project from. If not provided, the latest commit will be used.",
    )


class DiagnosticSeverity(IntEnum):
    Error = 1
    Warning = 2
    Information = 3
    Hint = 4


class DiagnosticTag(IntEnum):
    Unnecessary = 1
    Deprecated = 2


class Position(BaseModel):
    line: int
    character: int


class Range(BaseModel):
    start: Position
    end: Position


class Location(BaseModel):
    path: str = Field(validation_alias=AliasChoices("path", "uri"))
    range: Range

    def __str__(self) -> str:
        lines = (
            f"{self.range.start.line}"
            if self.range.start.line == self.range.end.line
            else f"{self.range.start.line}:{self.range.end.line}"
        )
        return f"{self.path}:{lines}"


class DiagnosticRelatedInformation(BaseModel):
    location: Location
    message: str


class CodeDescription(BaseModel):
    href: str


class Diagnostic(BaseModel):
    range: Range
    severity: Optional[DiagnosticSeverity] = None
    code: Optional[Union[int, str]] = None
    code_description: Optional[CodeDescription] = Field(
        default=None, serialization_alias="codeDescription"
    )
    source: Optional[str] = None
    message: str
    tags: Optional[List[DiagnosticTag]] = None
    related_information: Optional[List[DiagnosticRelatedInformation]] = Field(
        default=None, serialization_alias="relatedInformation"
    )
    data: Optional[Union[dict, list]] = None


class Line(BaseModel):
    number: int = Field(..., description="The line number.")
    content: str = Field(..., description="The content of the line.")


class File(BaseModel):
    path: FilePath = Field(..., description="The path of the file.")
    lines: list[Line] = Field(default_factory=list)
    diagnostics: List[Diagnostic] = Field(default_factory=list)

    @classmethod
    def from_content(cls, path: str, content: str) -> "File":
        return cls(
            path=path,
            lines=[
                Line(number=idx + 1, content=line)
                for idx, line in enumerate(content.splitlines())
            ],
        )

    def content(self) -> str:
        return "\n".join([line.content for line in self.lines]) + "\n"

    def insert_lines(self, start_line: int, content: str) -> "File":
        new_lines = content.splitlines()

        for idx, line in enumerate(new_lines):
            line_num = start_line + idx
            line_idx = line_num - 1
            self.lines.insert(line_idx, Line(number=line_num, content=line))

        for line in self.lines[start_line + len(new_lines) - 1 :]:
            line.number += len(new_lines)

        return self

    def replace_lines(self, start_line: int, end_line: int, content: str) -> "File":
        assert start_line < end_line, "start_line must be less than end_line"

        result = []
        new_lines = content.splitlines()

        result.extend(self.lines[: start_line - 1])

        for idx, line in enumerate(new_lines):
            line_num = start_line + idx
            result.append(Line(number=line_num, content=line))

        result.extend(self.lines[end_line - 1 :])

        for line in result[start_line + len(new_lines) - 1 :]:
            line.number += len(new_lines) - (end_line - start_line)

        self.lines = result
        return self

    def append_lines(self, content: str) -> "File":
        new_lines = content.splitlines()
        last_line = self.lines[-1] if self.lines else Line(number=0, content="")

        for idx, line in enumerate(new_lines):
            line_num = last_line.number + idx + 1
            line_idx = line_num - 1
            self.lines.insert(line_idx, Line(number=line_num, content=line))

        return self

    def __str__(self) -> str:
        output = []
        line_number_width = len(str(self.lines[-1].number))
        prev_line = 0

        output.append(f"{' ' * line_number_width} {UpperLeftCorner} {self.path}")

        for line in self.lines:
            if line.number != prev_line + 1:
                output.append(
                    f"{' ' * (line_number_width - 1)}{HorizontalEllipsis} {VerticalLine} {HorizontalEllipsis}"
                )

            output.append(
                f"{line.number:>{line_number_width}} {VerticalLine} {line.content}"
            )

            for diagnostic in self.diagnostics:
                line_index = line.number - 1
                if (
                    diagnostic.range.start.line
                    <= line_index
                    <= diagnostic.range.end.line
                ):
                    # Add carets
                    start = (
                        diagnostic.range.start.character
                        if line_index == diagnostic.range.start.line
                        else 0
                    )
                    end = (
                        diagnostic.range.end.character
                        if line_index == diagnostic.range.end.line
                        else len(line.content)
                    )

                    # Add diagnostic message
                    offset = " " * (start + line_number_width + 3)
                    caret_line = offset + "^" * (end - start)

                    severity = diagnostic.severity.name if diagnostic.severity else ""
                    output.append(f"{caret_line} {severity}: {diagnostic.message}")
                    output.append("")  # Add an empty line for readability

            prev_line = line.number

        output.append(f"{' ' * line_number_width} {LowerLeftCorner}")

        return "\n".join(output)


class Language(str, Enum):
    GO = "Go"
    JAVASCRIPT = "JavaScript"
    PYTHON = "Python"
    TYPESCRIPT = "TypeScript"


class CreateProjectRequest(BaseModel):
    repository: Repository = Field(
        ..., description="The repository to create the project from."
    )
    devcontainer: Optional[DevContainer] = Field(
        default=None,
        description="The dev container configuration to use for the project. If not provided, the configuration from the repository will be used. If the repository does not contain a dev container, the request will fail.",
    )
    languages: Optional[list[Language]] = Field(
        default=None,
        description="The languages to use for the project. If not provided, the languages will be inferred from the repository.",
    )


class Project(BaseModel):
    id: str = Field(..., description="The ID of the project.")


class TaskResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    stdout: str = Field(..., description="The standard output of the command.")
    stderr: str = Field(..., description="The standard error of the command.")
    exit_code: int = Field(
        ..., description="The exit code of the command.", alias="exitCode"
    )


class Task(BaseModel):
    alias: str = Field(..., description="The alias of the task.")
    command: str = Field(..., description="The shell command to run the task.")


class FileInfo(BaseModel):
    path: FilePath = Field(..., description="The path of the file.")


class FileUpdateType(str, Enum):
    UDIFF = "udiff"
    LINEDIFF = "linediff"
    OVERWRITE = "overwrite"


class UdiffUpdate(BaseModel):
    patch: str = Field(..., description="The patch to apply to the file.")


class LineDiffUpdate(BaseModel):
    start_line: int = Field(
        ...,
        description="The line number to start the diff from.",
        serialization_alias="startLine",
    )
    end_line: int = Field(
        ...,
        description="The line number to end the diff at, inclusive.",
        serialization_alias="endLine",
    )
    content: str = Field(..., description="The content of the diff.")


class OverwriteUpdate(BaseModel):
    content: str = Field(..., description="The new content of the file.")


class Symbol(BaseModel):
    name: str
    kind: str
    location: Location

    def __str__(self) -> str:
        return f"{self.name} ({self.kind.lower()}) at {self.location}"


class SearchMode(IntEnum):
    DEFAULT = 0
    EXACT = 1
    REGEX = 2
