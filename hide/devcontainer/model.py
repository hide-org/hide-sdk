from enum import Enum
from typing import Annotated, List, Union, Optional, Dict, Any, Mapping
from pydantic import BaseModel, Field, RootModel

LifeCycleCommand = Union[str, List[str], Mapping[str, Union[str, List[str]]]]


class ForwardPort(RootModel):
    root: Union[
        Annotated[int, Field(strict=True, ge=0, le=65535)],
        Annotated[str, Field(pattern=r"^([a-z0-9-]+):(\d{1,5})$")],
    ]


class AutoForwardAction(str, Enum):
    NOTIFY = "notify"
    OPEN_BROWSER = "openBrowser"
    OPEN_BROWSER_ONCE = "openBrowserOnce"
    OPEN_PREVIEW = "openPreview"
    SILENT = "silent"
    IGNORE = "ignore"


class PortProtocol(str, Enum):
    HTTP = "http"
    HTTPS = "https"


class PortAttributes(BaseModel):
    onAutoForward: Optional[AutoForwardAction] = Field(
        default=AutoForwardAction.NOTIFY,
        description="Defines the action that occurs when the port is discovered for automatic forwarding",
    )
    elevateIfNeeded: Optional[bool] = Field(
        default=False,
        description="Automatically prompt for elevation (if needed) when this port is forwarded. Elevate is required if the local port is a privileged port.",
    )
    label: Optional[str] = Field(
        default="Application",
        description="Label that will be shown in the UI for this port.",
    )
    requireLocalPort: Optional[bool] = Field(
        default=False,
        description="When true, a modal dialog will show if the chosen local port isn't used for forwarding.",
    )
    protocol: Optional[PortProtocol] = Field(
        default=None, description="The protocol to use when forwarding this port."
    )


class PortsAttributes(RootModel):
    root: Dict[
        Annotated[str, Field(strict=True, pattern=r"(^\d+(-\d+)?$)|(.+)")],
        PortAttributes,
    ] = Field(...)


class BuildOptions(BaseModel):
    target: Optional[str] = Field(
        default=None, description="Target stage in a multi-stage build."
    )
    args: Optional[Dict[str, str]] = Field(default=None, description="Build arguments.")
    cacheFrom: Optional[Union[str, List[str]]] = Field(
        default=None,
        description="The image to consider as a cache. Use an array to specify multiple images.",
    )


class WaitFor(str, Enum):
    INITIALIZE_COMMAND = "initializeCommand"
    ON_CREATE_COMMAND = "onCreateCommand"
    UPDATE_CONTENT_COMMAND = "updateContentCommand"
    POST_CREATE_COMMAND = "postCreateCommand"
    POST_START_COMMAND = "postStartCommand"


class UserEnvProbe(str, Enum):
    NONE = "none"
    LOGIN_SHELL = "loginShell"
    LOGIN_INTERACTIVE_SHELL = "loginInteractiveShell"
    INTERACTIVE_SHELL = "interactiveShell"


class HostRequirements(BaseModel):
    cpus: Optional[int] = Field(
        default=None, description="Number of required CPUs.", ge=1
    )
    memory: Optional[str] = Field(
        default=None,
        description="Amount of required RAM in bytes. Supports units tb, gb, mb and kb.",
        pattern=r"^\d+([tgmk]b)?$",
    )
    storage: Optional[str] = Field(
        default=None,
        description="Amount of required disk space in bytes. Supports units tb, gb, mb and kb.",
        pattern=r"^\d+([tgmk]b)?$",
    )
    gpu: Optional[Union[bool, str, Dict[str, Any]]] = Field(
        default=None,
        description='Indicates whether a GPU is required. The string "optional" indicates that a GPU is optional. An object value can be used to configure more detailed requirements.',
    )


class DevContainerCommon(BaseModel):
    name: Optional[str] = Field(
        default=None,
        description="A name for the dev container which can be displayed to the user.",
    )
    features: Optional[Dict[str, Any]] = Field(
        default=None, description="Features to add to the dev container."
    )
    overrideFeatureInstallOrder: Optional[List[str]] = Field(
        default=None,
        description="Array consisting of the Feature id (without the semantic version) of Features in the order the user wants them to be installed.",
    )
    forwardPorts: Optional[List[ForwardPort]] = Field(
        default=None,
        description='Ports that are forwarded from the container to the local machine. Can be an integer port number, or a string of the format "host:port_number".',
    )
    portsAttributes: Optional[PortsAttributes] = Field(
        default=None,
        description="Set default properties that are applied when a specific port number is forwarded.",
    )
    otherPortsAttributes: Optional[PortAttributes] = Field(
        default=None,
        description="Set default properties that are applied to all ports that don't get properties from the setting `remote.portsAttributes`.",
    )
    updateRemoteUserUID: Optional[bool] = Field(
        default=None,
        description="Controls whether on Linux the container's user should be updated with the local user's UID and GID. On by default when opening from a local folder.",
    )
    remoteEnv: Optional[Dict[str, Optional[str]]] = Field(
        default=None,
        description="Remote environment variables to set for processes spawned in the container including lifecycle scripts and any remote editor/IDE server process.",
    )
    remoteUser: Optional[str] = Field(
        default=None,
        description="The username to use for spawning processes in the container including lifecycle scripts and any remote editor/IDE server process. The default is the same user as the container.",
    )
    initializeCommand: Optional[Union[str, List[str]]] = Field(
        default=None,
        description='A command string or list of command arguments to run on the host machine during initialization, including during container creation and on subsequent starts. The command may run more than once during a given session. This command is run before "onCreateCommand". If this is a single string, it will be run in a shell. If this is an array of strings, it will be run as a single command without shell.',
    )
    onCreateCommand: Optional[LifeCycleCommand] = Field(
        default=None,
        description='A command to run when creating the container. This command is run after "initializeCommand" and before "updateContentCommand". If this is a single string, it will be run in a shell. If this is an array of strings, it will be run as a single command without shell.',
    )
    updateContentCommand: Optional[LifeCycleCommand] = Field(
        default=None,
        description='A command to run when creating the container and rerun when the workspace content was updated while creating the container. This command is run after "onCreateCommand" and before "postCreateCommand". If this is a single string, it will be run in a shell. If this is an array of strings, it will be run as a single command without shell.',
    )
    postCreateCommand: Optional[LifeCycleCommand] = Field(
        default=None,
        description='A command to run after creating the container. This command is run after "updateContentCommand" and before "postStartCommand". If this is a single string, it will be run in a shell. If this is an array of strings, it will be run as a single command without shell.',
    )
    postStartCommand: Optional[LifeCycleCommand] = Field(
        default=None,
        description='A command to run after starting the container. This command is run after "postCreateCommand" and before "postAttachCommand". If this is a single string, it will be run in a shell. If this is an array of strings, it will be run as a single command without shell.',
    )
    postAttachCommand: Optional[LifeCycleCommand] = Field(
        default=None,
        description='A command to run when attaching to the container. This command is run after "postStartCommand". If this is a single string, it will be run in a shell. If this is an array of strings, it will be run as a single command without shell.',
    )
    waitFor: Optional[WaitFor] = Field(
        default=None,
        description='The user command to wait for before continuing execution in the background while the UI is starting up. The default is "updateContentCommand".',
    )
    userEnvProbe: Optional[UserEnvProbe] = Field(
        default=None,
        description='User environment probe to run. The default is "loginInteractiveShell".',
    )
    hostRequirements: Optional[HostRequirements] = Field(
        default=None, description="Host hardware requirements."
    )
    customizations: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Tool-specific configuration. Each tool should use a JSON object subproperty with a unique name to group its customizations.",
    )
    additionalProperties: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional properties"
    )


class ContainerShutdownAction(str, Enum):
    NONE = "none"
    STOP_CONTAINER = "stopContainer"


class NonComposeBase(BaseModel):
    appPort: Optional[Union[int, str, List[Union[int, str]]]] = Field(
        default=None,
        description="Application ports that are exposed by the container. This can be a single port or an array of ports. Each port can be a number or a string. A number is mapped to the same port on the host. A string is passed to Docker unchanged and can be used to map ports differently, e.g. '8000:8010'.",
    )
    containerEnv: Optional[Dict[str, str]] = Field(
        default=None, description="Container environment variables."
    )
    containerUser: Optional[str] = Field(
        default=None,
        description="The user the container will be started with. The default is the user on the Docker image.",
    )
    mounts: Optional[List[str]] = Field(
        default=None,
        description="Mount points to set up when creating the container. See Docker's documentation for the --mount option for the supported syntax.",
    )
    runArgs: Optional[List[str]] = Field(
        default=None,
        description="The arguments required when starting in the container.",
    )
    shutdownAction: Optional[ContainerShutdownAction] = Field(
        default=None,
        description="Action to take when the user disconnects from the container in their editor. The default is to stop the container.",
    )
    overrideCommand: Optional[bool] = Field(
        default=None,
        description="Whether to overwrite the command specified in the image. The default is true.",
    )
    workspaceFolder: Optional[str] = Field(
        default=None,
        description="The path of the workspace folder inside the container.",
    )
    workspaceMount: Optional[str] = Field(
        default=None,
        description="The --mount parameter for docker run. The default is to mount the project folder at /workspaces/$project.",
    )


class DockerfileContainer(BaseModel):
    dockerfile: str = Field(
        ...,
        description="The location of the Dockerfile that defines the contents of the container. The path is relative to the folder containing the `devcontainer.json` file.",
    )
    context: Optional[str] = Field(
        default=None,
        description="The location of the context folder for building the Docker image. The path is relative to the folder containing the `devcontainer.json` file.",
    )
    build: Optional[BuildOptions] = Field(
        default=None, description="Docker build-related options."
    )


class ImageContainer(BaseModel):
    image: str = Field(
        ..., description="The docker image that will be used to create the container."
    )


class ComposeShutdownAction(str, Enum):
    NONE = "none"
    STOP_COMPOSE = "stopCompose"


class ComposeContainer(BaseModel):
    dockerComposeFile: Union[str, List[str]] = Field(
        ...,
        description="The name of the docker-compose file(s) used to start the services.",
    )
    service: str = Field(
        ...,
        description="The service you want to work on. This is considered the primary container for your dev environment which your editor will connect to.",
    )
    runServices: Optional[List[str]] = Field(
        default=None,
        description="An array of services that should be started and stopped.",
    )
    workspaceFolder: str = Field(
        ...,
        description="The path of the workspace folder inside the container. This is typically the target path of a volume mount in the docker-compose.yml.",
    )
    shutdownAction: Optional[ComposeShutdownAction] = Field(
        default=None,
        description="Action to take when the user disconnects from the primary container in their editor. The default is to stop all of the compose containers.",
    )
    overrideCommand: Optional[bool] = Field(
        default=None,
        description="Whether to overwrite the command specified in the image. The default is false.",
    )


class DockerfileDevContainer(DockerfileContainer, NonComposeBase, DevContainerCommon):
    pass


class ImageDevContainer(ImageContainer, NonComposeBase, DevContainerCommon):
    pass


class ComposeDevContainer(ComposeContainer, DevContainerCommon):
    pass

DevContainer = Union[DockerfileDevContainer, ImageDevContainer, ComposeDevContainer]

class DevContainerRoot(RootModel):
    root: DevContainer = Field(
        ..., description="The root of the dev container configuration."
    )
