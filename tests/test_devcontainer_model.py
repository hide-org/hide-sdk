import pytest
from pydantic import ValidationError
from hide.devcontainer.model import (
    ForwardPort, AutoForwardAction, PortProtocol, PortAttributes, PortsAttributes,
    BuildOptions, WaitFor, UserEnvProbe, HostRequirements, DevContainerCommon,
    ContainerShutdownAction, NonComposeBase, DockerfileContainer, ImageContainer,
    ComposeShutdownAction, ComposeContainer, DockerfileDevContainer, ImageDevContainer,
    ComposeDevContainer, DevContainerRoot
)

def test_forward_port_int():
    port = ForwardPort(root=8080)
    assert port.root == 8080

def test_forward_port_str():
    port = ForwardPort(root="localhost:8080")
    assert port.root == "localhost:8080"

def test_forward_port_invalid():
    with pytest.raises(ValidationError):
        ForwardPort(root="invalid_port")

def test_auto_forward_action():
    assert AutoForwardAction.NOTIFY == "notify"
    assert AutoForwardAction.OPEN_BROWSER == "openBrowser"

def test_port_protocol():
    assert PortProtocol.HTTP == "http"
    assert PortProtocol.HTTPS == "https"

def test_port_attributes_defaults():
    attrs = PortAttributes()
    assert attrs.onAutoForward == AutoForwardAction.NOTIFY
    assert attrs.elevateIfNeeded == False
    assert attrs.label == "Application"
    assert attrs.requireLocalPort == False
    assert attrs.protocol is None

def test_ports_attributes():
    attrs = PortsAttributes(root={"8080": PortAttributes()})
    assert "8080" in attrs.root

def test_build_options_defaults():
    options = BuildOptions()
    assert options.target is None
    assert options.args is None
    assert options.cacheFrom is None

def test_wait_for():
    assert WaitFor.INITIALIZE_COMMAND == "initializeCommand"
    assert WaitFor.POST_START_COMMAND == "postStartCommand"

def test_user_env_probe():
    assert UserEnvProbe.NONE == "none"
    assert UserEnvProbe.LOGIN_SHELL == "loginShell"

def test_host_requirements_defaults():
    reqs = HostRequirements()
    assert reqs.cpus is None
    assert reqs.memory is None
    assert reqs.storage is None
    assert reqs.gpu is None

def test_dev_container_common_defaults():
    common = DevContainerCommon()
    assert common.name is None
    assert common.features is None
    assert common.overrideFeatureInstallOrder is None
    assert common.forwardPorts is None
    assert common.portsAttributes is None
    assert common.otherPortsAttributes is None
    assert common.updateRemoteUserUID is None
    assert common.remoteEnv is None
    assert common.remoteUser is None
    assert common.initializeCommand is None
    assert common.onCreateCommand is None
    assert common.updateContentCommand is None
    assert common.postCreateCommand is None
    assert common.postStartCommand is None
    assert common.postAttachCommand is None
    assert common.waitFor is None
    assert common.userEnvProbe is None
    assert common.hostRequirements is None
    assert common.customizations is None
    assert common.additionalProperties is None

def test_container_shutdown_action():
    assert ContainerShutdownAction.NONE == "none"
    assert ContainerShutdownAction.STOP_CONTAINER == "stopContainer"

def test_non_compose_base_defaults():
    base = NonComposeBase()
    assert base.appPort is None
    assert base.containerEnv is None
    assert base.containerUser is None
    assert base.mounts is None
    assert base.runArgs is None
    assert base.shutdownAction is None
    assert base.overrideCommand is None
    assert base.workspaceFolder is None
    assert base.workspaceMount is None

def test_dockerfile_container():
    container = DockerfileContainer(dockerfile="Dockerfile")
    assert container.dockerfile == "Dockerfile"
    assert container.context is None
    assert container.build is None

def test_image_container():
    container = ImageContainer(image="myimage")
    assert container.image == "myimage"

def test_compose_shutdown_action():
    assert ComposeShutdownAction.NONE == "none"
    assert ComposeShutdownAction.STOP_COMPOSE == "stopCompose"

def test_compose_container():
    container = ComposeContainer(
        dockerComposeFile="docker-compose.yml",
        service="web",
        workspaceFolder="/workspace"
    )
    assert container.dockerComposeFile == "docker-compose.yml"
    assert container.service == "web"
    assert container.workspaceFolder == "/workspace"
    assert container.runServices is None
    assert container.shutdownAction is None
    assert container.overrideCommand is None

def test_dockerfile_dev_container():
    container = DockerfileDevContainer(dockerfile="Dockerfile")
    assert container.dockerfile == "Dockerfile"

def test_image_dev_container():
    container = ImageDevContainer(image="myimage")
    assert container.image == "myimage"

def test_compose_dev_container():
    container = ComposeDevContainer(
        dockerComposeFile="docker-compose.yml",
        service="web",
        workspaceFolder="/workspace"
    )
    assert container.dockerComposeFile == "docker-compose.yml"
    assert container.service == "web"
    assert container.workspaceFolder == "/workspace"

def test_dev_container_root():
    root = DevContainerRoot(root=DockerfileDevContainer(dockerfile="Dockerfile"))
    assert isinstance(root.root, DockerfileDevContainer)
    assert root.root.dockerfile == "Dockerfile"


import json
from pydantic import ValidationError

def test_dev_container_root_from_dockerfile():
    json_data = '''
    {
        "dockerfile": "Dockerfile"
    }
    '''
    root = DevContainerRoot.model_validate(json.loads(json_data))
    assert isinstance(root.root, DockerfileDevContainer)
    assert root.root.dockerfile == "Dockerfile"

def test_dev_container_root_from_image():
    json_data = '''
    {
        "image": "myimage"
    }
    '''
    root = DevContainerRoot.model_validate(json.loads(json_data))
    assert isinstance(root.root, ImageDevContainer)
    assert root.root.image == "myimage"

def test_dev_container_root_from_compose():
    json_data = '''
    {
        "dockerComposeFile": "docker-compose.yml",
        "service": "web",
        "workspaceFolder": "/workspace"
    }
    '''
    root = DevContainerRoot.model_validate(json.loads(json_data))
    assert isinstance(root.root, ComposeDevContainer)
    assert root.root.dockerComposeFile == "docker-compose.yml"
    assert root.root.service == "web"
    assert root.root.workspaceFolder == "/workspace"

def test_dev_container_root_invalid_field():
    json_data = '''
    {
        "invalidField": "invalidValue"
    }
    '''
    with pytest.raises(ValidationError):
        DevContainerRoot.model_validate(json.loads(json_data))

def test_dev_container_root_missing_field():
    json_data = '''
    {
        "dockerComposeFile": "docker-compose.yml",
        "service": "web"
    }
    '''
    with pytest.raises(ValidationError):
        DevContainerRoot.model_validate(json.loads(json_data))
