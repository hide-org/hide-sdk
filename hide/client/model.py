from typing import List, Union, Optional, Dict, Any
from pydantic import BaseModel, Field, conint, constr, root_validator


class Features(BaseModel):
    __root__: Dict[str, Any]


class PortAttributes(BaseModel):
    onAutoForward: Optional[
        constr(regex="^(notify|openBrowser|openBrowserOnce|openPreview|silent|ignore)$")
    ] = Field("notify", description="Defines the action that occurs when the port is discovered for automatic forwarding")
    elevateIfNeeded: Optional[bool] = Field(False, description="Automatically prompt for elevation (if needed) when this port is forwarded. Elevate is required if the local port is a privileged port.")
    label: Optional[str] = Field("Application", description="Label that will be shown in the UI for this port.")
    requireLocalPort: Optional[bool] = Field(False, description="When true, a modal dialog will show if the chosen local port isn't used for forwarding.")
    protocol: Optional[constr(regex="^(http|https)$")] = Field(None, description="The protocol to use when forwarding this port.")


class PortsAttributes(BaseModel):
    __root__: Dict[constr(regex=r"(^\d+(-\d+)?$)|(.+)"), PortAttributes]


class RemoteEnv(BaseModel):
    __root__: Dict[str, Optional[str]]


class BuildOptions(BaseModel):
    target: Optional[str] = Field(None, description="Target stage in a multi-stage build.")
    args: Optional[Dict[str, str]] = Field(None, description="Build arguments.")
    cacheFrom: Optional[Union[str, List[str]]] = Field(None, description="The image to consider as a cache. Use an array to specify multiple images.")


class DevContainerCommon(BaseModel):
    name: Optional[str] = Field(None, description="A name for the dev container which can be displayed to the user.")
    features: Optional[Features] = Field(None, description="Features to add to the dev container.")
    overrideFeatureInstallOrder: Optional[List[str]] = Field(None, description="Array consisting of the Feature id (without the semantic version) of Features in the order the user wants them to be installed.")
    forwardPorts: Optional[List[Union[conint(ge=0, le=65535), constr(regex=r"^([a-z0-9-]+):(\d{1,5})$")]]] = Field(None, description='Ports that are forwarded from the container to the local machine. Can be an integer port number, or a string of the format "host:port_number".')
    portsAttributes: Optional[PortsAttributes] = Field(None, description='Set default properties that are applied when a specific port number is forwarded.')
    otherPortsAttributes: Optional[PortAttributes] = Field(None, description='Set default properties that are applied to all ports that don\'t get properties from the setting `remote.portsAttributes`.')
    updateRemoteUserUID: Optional[bool] = Field(None, description="Controls whether on Linux the container's user should be updated with the local user's UID and GID. On by default when opening from a local folder.")
    remoteEnv: Optional[RemoteEnv] = Field(None, description="Remote environment variables to set for processes spawned in the container including lifecycle scripts and any remote editor/IDE server process.")
    remoteUser: Optional[str] = Field(None, description="The username to use for spawning processes in the container including lifecycle scripts and any remote editor/IDE server process. The default is the same user as the container.")
    initializeCommand: Optional[Union[str, List[str]]] = Field(None, description='A command string or list of command arguments to run on the host machine during initialization, including during container creation and on subsequent starts. The command may run more than once during a given session. This command is run before "onCreateCommand". If this is a single string, it will be run in a shell. If this is an array of strings, it will be run as a single command without shell.')
    onCreateCommand: Optional[Union[str, List[str], Dict[str, Union[str, List[str]]]]] = Field(None, description='A command to run when creating the container. This command is run after "initializeCommand" and before "updateContentCommand". If this is a single string, it will be run in a shell. If this is an array of strings, it will be run as a single command without shell.')
    updateContentCommand: Optional[Union[str, List[str], Dict[str, Union[str, List[str]]]]] = Field(None, description='A command to run when creating the container and rerun when the workspace content was updated while creating the container. This command is run after "onCreateCommand" and before "postCreateCommand". If this is a single string, it will be run in a shell. If this is an array of strings, it will be run as a single command without shell.')
    postCreateCommand: Optional[Union[str, List[str], Dict[str, Union[str, List[str]]]]] = Field(None, description='A command to run after creating the container. This command is run after "updateContentCommand" and before "postStartCommand". If this is a single string, it will be run in a shell. If this is an array of strings, it will be run as a single command without shell.')
    postStartCommand: Optional[Union[str, List[str], Dict[str, Union[str, List[str]]]]] = Field(None, description='A command to run after starting the container. This command is run after "postCreateCommand" and before "postAttachCommand". If this is a single string, it will be run in a shell. If this is an array of strings, it will be run as a single command without shell.')
    postAttachCommand: Optional[Union[str, List[str], Dict[str, Union[str, List[str]]]]] = Field(None, description='A command to run when attaching to the container. This command is run after "postStartCommand". If this is a single string, it will be run in a shell. If this is an array of strings, it will be run as a single command without shell.')
    waitFor: Optional[constr(regex="^(initializeCommand|onCreateCommand|updateContentCommand|postCreateCommand|postStartCommand)$")] = Field(None, description='The user command to wait for before continuing execution in the background while the UI is starting up. The default is "updateContentCommand".')
    userEnvProbe: Optional[constr(regex="^(none|loginShell|loginInteractiveShell|interactiveShell)$")] = Field(None, description='User environment probe to run. The default is "loginInteractiveShell".')
    hostRequirements: Optional[Dict[str, Any]] = Field(None, description="Host hardware requirements.")
    customizations: Optional[Dict[str, Any]] = Field(None, description="Tool-specific configuration. Each tool should use a JSON object subproperty with a unique name to group its customizations.")
    additionalProperties: Optional[Dict[str, Any]] = Field(None, description="Additional properties")


class NonComposeBase(BaseModel):
    appPort: Optional[Union[int, str, List[Union[int, str]]]] = Field(None, description="Application ports that are exposed by the container. This can be a single port or an array of ports. Each port can be a number or a string. A number is mapped to the same port on the host. A string is passed to Docker unchanged and can be used to map ports differently, e.g. '8000:8010'.")
    containerEnv: Optional[Dict[str, str]] = Field(None, description="Container environment variables.")
    containerUser: Optional[str] = Field(None, description="The user the container will be started with. The default is the user on the Docker image.")
    mounts: Optional[List[str]] = Field(None, description="Mount points to set up when creating the container. See Docker's documentation for the --mount option for the supported syntax.")
    runArgs: Optional[List[str]] = Field(None, description="The arguments required when starting in the container.")
    shutdownAction: Optional[constr(regex="^(none|stopContainer)$")] = Field(None, description="Action to take when the user disconnects from the container in their editor. The default is to stop the container.")
    overrideCommand: Optional[bool] = Field(None, description="Whether to overwrite the command specified in the image. The default is true.")
    workspaceFolder: Optional[str] = Field(None, description="The path of the workspace folder inside the container.")
    workspaceMount: Optional[str] = Field(None, description="The --mount parameter for docker run. The default is to mount the project folder at /workspaces/$project.")


class DockerfileContainer(BaseModel):
    dockerfile: str = Field(..., description="The location of the Dockerfile that defines the contents of the container. The path is relative to the folder containing the `devcontainer.json` file.")
    context: Optional[str] = Field(None, description="The location of the context folder for building the Docker image. The path is relative to the folder containing the `devcontainer.json` file.")
    build: Optional[BuildOptions] = Field(None, description="Docker build-related options.")


class ImageContainer(BaseModel):
    image: str = Field(..., description="The docker image that will be used to create the container.")


class ComposeContainer(BaseModel):
    dockerComposeFile: Union[str, List[str]] = Field(..., description="The name of the docker-compose file(s) used to start the services.")
    service: str = Field(..., description="The service you want to work on. This is considered the primary container for your dev environment which your editor will connect to.")
    runServices: Optional[List[str]] = Field(None, description="An array of services that should be started and stopped.")
    workspaceFolder: str = Field(..., description="The path of the workspace folder inside the container. This is typically the target path of a volume mount in the docker-compose.yml.")
    shutdownAction: Optional[constr(regex="^(none|stopCompose)$")] = Field(None, description="Action to take when the user disconnects from the primary container in their editor. The default is to stop all of the compose containers.")
    overrideCommand: Optional[bool] = Field(None, description="Whether to overwrite the command specified in the image. The default is false.")

class DevContainer(BaseModel):
    dev_container_common: Optional[DevContainerCommon] = Field(None)
    non_compose_base: Optional[NonComposeBase] = Field(None)
    dockerfile_container: Optional[DockerfileContainer] = Field(None)
    image_container: Optional[ImageContainer] = Field(None)
    compose_container: Optional[ComposeContainer] = Field(None)

    @root_validator
    def check_configurations(cls, values):
        compose_container = values.get('compose_container')
        dockerfile_container = values.get('dockerfile_container')
        image_container = values.get('image_container')
        non_compose_base = values.get('non_compose_base')

        if compose_container and (dockerfile_container or image_container or non_compose_base):
            raise ValueError("Cannot have 'compose_container' with 'dockerfile_container', 'image_container', or 'non_compose_base' in the same configuration.")
        if dockerfile_container and image_container:
            raise ValueError("Cannot have both 'dockerfile_container' and 'image_container' in the same configuration.")
        if non_compose_base and not (dockerfile_container or image_container):
            raise ValueError("'non_compose_base' can only be used with 'dockerfile_container' or 'image_container'.")
        return values
