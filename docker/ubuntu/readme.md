# Running ZMS in a Docker container with Ubuntu

Important: *The here presented Docker environment is not recommended for production, just for testing and exploration.*

The ZMS source folder `./docker` contains two minimalistic Docker files: 
1. the [dockerfile](https://github.com/zms-publishing/ZMS/blob/main/docker/ubuntu/dockerfile) for creating a Docker *image* and 
2. the [docker-compose](https://github.com/zms-publishing/ZMS/blob/main/docker/ubuntu/docker-compose.yml) file for building a Docker *container*.

The image utilizes a minimal *Ubuntu 24.04*-Linux with a fresh compiled Python3 and some additional software packages (like mariadb and openldap). The ZMS installation happens with pip in a successively created virtual python environment (`/home/zope/venv`) and provides the ZMS code in the pip-"editable" mode. Both the ZMS source code (`/home/zope/venv/src/ZMS/.git`) and the Zope instance are placed in the virtual python environment folder (`/home/zope/venv/instance/zms5`)

To make Zope running there are some crucial config files needed which usually (created by `mkwsgiinstance`) are set on default values. In a Docker environment these defaults must be modified; moreover the setup contains a ZEO-server for running multiple Zope processes in parallel (e.g. for debugging). That is why a small set of config files is provided as presets via the the source-folders
1. ./docker/var
2. ./docker/etc
3. ./docker/Extensions

These sources will be copied into the *image* (on building) 
```yaml
# dockerfile
COPY ./etc venv/instance/zms5/etc
COPY ./var venv/instance/zms5/var
COPY ./Extensions venv/instance/zms5/Extensions
```
or referenced as *volume mounts* from the *container* (on composing):
```yaml
# docker-compose
    volumes:
      - ./etc/:/home/zope/venv/instance/zms5/etc/
      - ./var/:/home/zope/venv/instance/zms5/var/
      - ./Extensions/: /home/zope/venv/instance/zms5/Extensions
```


## Overview of Docker- and all Zope config-files

*Hint: to ease the file access from the container the config files are not restricted:* `chmod -r 777`
```
$ tree -p
.
├── [-rw-r--r--]  docker-compose.yml
├── [-rw-r--r--]  dockerfile
├── [drwxrwxrwx]  Extensions
├── [drwxrwxrwx]  etc
│   ├── [-rwxrwxrwx]  start.sh
│   ├── [-rwxrwxrwx]  zeo.conf
│   ├── [-rwxrwxrwx]  zope.conf
│   └── [-rwxrwxrwx]  zope.ini
└── [drwxrwxrwx]  var
    ├── [-rwxrwxrwx]  Data.fs
    ├── [-rwxrwxrwx]  Data.fs.index
    ├── [-rwxrwxrwx]  Data.fs.lock
    ├── [-rwxrwxrwx]  Data.fs.tmp
    ├── [-rwxrwxrwx]  Z4.pid
    ├── [drwxrwxrwx]  cache
    ├── [drwxrwxrwx]  log
    │   ├── [-rwxrwxrwx]  Z4.log
    │   ├── [-rwxrwxrwx]  event.log
    │   └── [-rwxrwxrwx]  zeo.log
    └── [srwxrwxrwx]  zeosocket
```

## Running the ZMS Container with VSCode

The VSCode Docker Extension [ms-azuretools.vscode-docker](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker) is a perfect tool for handling containers. A right mouse click on the file ´docker-compose.yaml´ starts composing the container. Initially ZEO will be started and Zope will run on port 8085.

![Running the ZMS Container with VSCode](../../docs/images/admin_docker_run.gif)

## Attach VSCode to the ZMS Container
Another right click on the running container-ID allows to intrude the container with VSCode and launch a new Zope instance in debugging mode. 
Hint: For this purpose the  docker-container folder `/home/zope/venv/src/zms/docker/.vscode/` contains a prepared VSCode-workspace file and a launch file for starting Zope in debug-mode within the container  [launch.json](https://github.com/zms-publishing/ZMS/blob/main/docker/.vscode/launch.json). The thus launched Zope instance will run port 8087.

![Attach VSCode to the ZMS Container](../../docs/images/admin_docker_debug_zeo.gif)