import hide
from hide.devcontainer.model import ImageDevContainer
from hide.model import Repository
from hide.toolkit import Toolkit

hide_client = hide.Client()

project = hide_client.create_project(
    repository=Repository(url="https://github.com/your-org/your-repo.git"),
    devcontainer=ImageDevContainer(
        image="mcr.microsoft.com/devcontainers/python:3.12",
        onCreateCommand="pip install -r requirements.txt",
        customizations={
            "hide": {
                "tasks": [
                    {"alias": "test", "command": "poetry run pytest"},
                    {"alias": "run", "command": "poetry run uvicorn main:main"},
                ]
            }
        },
    ),
)

toolkit = Toolkit(project=project, client=hide_client)

your_agent.with_tools(toolkit).run("Do stuff")
