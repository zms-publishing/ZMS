# Running ZMS in a Docker container

Important: *The presented Docker environment is not yet recommended for production, just for testing and exploration.* We do plan to evolve these to be production ready, but we are not there yet.

The ZMS source folder `./docker` contains two minimalistic Docker files:

1. the [Dockerfile](zms-base/Dockerfile) for creating a Docker *image* and
2. the [docker-compose.yml](../docker-compose.yml) file for building the Docker *containers*.

The image utilizes a Linux with a fresh Python3 and some additional software packages (like mariadb and openldap). The ZMS installation happens with pip in a virtual python environment (`/home/zope/venv`) and provides the ZMS code in the pip-"editable" mode. Both the ZMS source code (`/home/zope/venv/src/ZMS/.git`) and the Zope instance are placed in the virtual python environment folder (`/home/zope/`)

To make Zope running there are some crucial config files needed which usually (created by `mkwsgiinstance`) are set on default values. In a Docker environment these defaults must be modified; moreover the setup contains a ZEO-server for running multiple Zope processes in parallel (e.g. for debugging). That is why a small set of config files is provided as presets via  the the source-folders
1. ./docker/{zope,zeo}/etc
1. ./docker/{zope,zeo}/var
1. ./docker/zope/Extensions

These sources are mapped into the respective *containers*

## Overview of Docker- and all Zope config-files

*Hint: to ease the file access from the container the config files are not restricted:* `chmod -R 777 ./docker/`

## Running the ZMS Container with VSCode

The VSCode Docker Extension [ms-azuretools.vscode-docker](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker) is a perfect tool for handling containers. A right mouse click on the file ´docker-compose.yaml´ starts composing the container. Initially ZEO will be started and Zope will run on http://localhost/, the management interface on http://admin:admin@localhost/manage_main.

![Running the ZMS Container with VSCode](../docs/images/admin_docker_run.gif)

## Attach VSCode to the ZMS Container

Another right click on the running container-ID allows to intrude the container with VSCode and launch a new Zope instance in debugging mode.
Hint: For this purpose the  docker-container folder `/home/zope/venv/src/zms/docker/.vscode/` contains a prepared VSCode-workspace file and a launch file for starting Zope in debug-mode within the container  [launch.json](https://github.com/zms-publishing/ZMS/blob/main/docker/.vscode/launch.json). The thus launched Zope instance will run port 8087.

![Attach VSCode to the ZMS Container](../docs/images/admin_docker_debug_zeo.gif)
