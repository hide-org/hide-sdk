# Hide: Headless IDE for Coding Agents

Hide is a headless Integrated Development Environment (IDE) designed for coding agents. It provides a robust toolkit for managing projects, running tasks, and handling files within a project.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Installation

`pip install hide-py`

### From sources

To install the Hide project, you need to have Python 3.12 or higher. You can install the dependencies using [Poetry](https://python-poetry.org/).

1. Clone the repository:
    ```sh
    git clone https://github.com/artmoskvin/hide-python.git
    cd hide-python
    ```

2. Install the dependencies and Hide in editable mode:
    ```sh
    poetry install
    ```

## Usage

### HideClient

The `HideClient` class provides methods to interact with the Hide server. Here are some examples of how to use it:

```python
import hide
from hide.model import Repository
from hide.devcontainer.model import ImageDevContainer

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

print(f"Project ID: {project.id}")
```

## Testing

To run the tests, use the following command:

```sh
poetry run pytest
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.