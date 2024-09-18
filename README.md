# Hide: Headless IDE for Coding Agents

Hide is a headless Integrated Development Environment (IDE) designed for coding agents. It provides a robust toolkit for managing projects, running tasks, and handling files within a project.

## Table of Contents

-   [Requirements](#requirements)
-   [Installation](#installation)
-   [Usage](#usage)
-   [Testing](#testing)
-   [Contributing](#contributing)
-   [License](#license)

## Requirements

-   Python 3.10+
-   Hide Runtime: https://github.com/hide-org/hide

## Installation

`pip install hide-py`

### From sources

To install Hide from sources, you need [Poetry](https://python-poetry.org/).

1. Clone the repository:

    ```sh
    git clone git@github.com:hide-org/hide-sdk.git
    cd hide-sdk
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

## Releases

To release a new version, follow these steps:

1. Update the version in `pyproject.toml`. Try to follow [Semantic Versioning](https://semver.org/).
2. Commit the changes with the message "Release vX.Y.Z" and open a pull request.
3. After the pull request is merged, create a new release using the GitHub UI or the command line. For example, to create a new release with the command line, run the following command:

    ```bash
    gh release create vX.Y.Z --title "hide-py vX.Y.Z" --generate-notes
    ```

    Replace `X.Y.Z` with the new version number.

    For additional options and for UI instructions, refer to the [GitHub documentation](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository).

4. The release will trigger a GitHub Actions workflow that will publish the package to PyPI. Monitor the workflow for any errors or warnings.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
