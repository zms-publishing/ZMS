# ZMS Installation

## Prerequisites
The following setup is working on Ubuntu 20.4. and will run in a similar way on other unix-like operating systems (as well as *Windows Sublinux*, WSL). It is recomended to add a special non-root user like _zope_ for running the zope application server.
ZMS needs a Python version 3.6+; please check your installed python version
```console
~$: python3 --version
```
and update or reinstall Python3, if it is missing or a former Python version is installed.
ZMS is running on Zope (Version 5+) as the underlaying Python3 application server. The ZMS setup routine automatically installs Zope. Zope needs some basic OS packages for communication and compiling; the following packages should be installed on your system:
```console
~$: sudo apt-get install gcc
~$: sudo apt-get install openssh-server
~$: sudo apt-get install build-essential 
~$: sudo apt-get install libssl-dev libffi-dev 
~$: sudo apt-get install python3-dev
~$: sudo apt-get install python3-venv
~$: sudo apt-get install git
```

## 1. Setup virtual Python environment
The first step is to setup a virtual Python environment which is a kind of copy of the primary Python installation which easily can be extended or replaced. The following example places the virtual environment into the home-folder of user _zope_:
```console
~$: python3 -m venv /home/zope/vpy3
```
## 2. Install ZMS into the virtual Python environment
After changing to the `bin`-folder of the installed virtual environment, simply install ZMS with `pip` from the ZMS-github-master: https://github.com/zms-publishing/ZMS5
```console
~$: cd /home/zope/vpy3/bin/
~$: ./pip install https://github.com/zms-publishing/ZMS5/archive/master.zip
```
## 3. Add new Zope instance
After the ZMS installation the bin-folder of the virtual environment contains a lot of new scipts. Please use `mkwsgiinstance` to generate an new zope-instance, named zms5_dev as an example:
```console
~$: ./mkwsgiinstance -d /home/zope/instance/zms5_dev
```
More: https://zope.readthedocs.io/en/latest/operation.html#creating-a-zope-instance

## 4. Start Zope server (default port 8080)
```console
~$: ./runwsgi -v /home/zope/instance/zms5_dev/etc/zope.ini
```
More: https://zope.readthedocs.io/en/latest/operation.html#running-zope

## 5. Add a new ZMS node into Zope object tree
The _add menu_ is located in the Zope top bar. Please select the object type 'ZMS' to add a new ZMS node into the Zope object tree. After initializing the new ZMS node you will change to the ZMS-GUI and see a default content tree:

![Add ZMS](images/develop_add_zmsnode.gif)
*Adding a an ZMS instance and getting a first glance of the ZMS GUI*

<br/>

# Working with Visual Studio Code
## Installation & Setup of Visual Studio Code
[Visual Studio Code](https://code.visualstudio.com/) (VS Code) is a free source-code editor made by Microsoft for Windows, Linux and macOS - and a perfect environment for developing ZMS websites. On linux you can install VS Code by running:
```console
sudo snap install --classic code
```
![Install VS Code](images/develop_vscode_install.gif)

After completing the standard installation of VS Code at least two helpful **extensions** should be added:

1. [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python) for syntax highlighting and debugging Python code
2. [Remote Development Extension Pack](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack) for getting SSH-connections to  remote servers, VMs or the Sublinux on your Windows 10 machine.

The [ZMS code repository](https://github.com/zms-publishing/ZMS5/) contains a basic set of customizable VS Code JSON config files for the workspace and for running Zope/ZMS in the debugging mode:
```
.vscode
	ZMS5.code-workspace
	launch.json
	settings.json
```

### ZMS5.code-workspace
[ZMS5.code-workspace](https://github.com/zms-publishing/ZMS5/blob/master/.vscode/ZMS5.code-workspace) defines some workspace parameters like
+ shown folders
+ python path
+ files associations
+ invisible files
+ VS Code theme & icons

### settings.json
The only item in [settings.json](https://github.com/zms-publishing/ZMS5/blob/master/.vscode/settings.json) tells VS Code where to expect the python executable. This should be the one of the virtual python (and not the primary python installation)

### launch.json
The file [launch.json](https://github.com/zms-publishing/ZMS5/blob/master/.vscode/launch.json) is the most important config file bedause it tells VS Code how the Python extension will start the debugger. So all relevant paths must be mentioned, especially the starting `programm` and the `env`ironment variables Zope needs for starting a Zope instance. The following example config file assumes that 
1. there is a user `zope` using its home folder as a location for the virtual python (`~/vpy3/`) and the zope instances (`~/instance/`)
2. the name of the Zope instance is `zms5_dev`
3. the git-cloned code of Zope and ZMS are placed in a source folder called `~/src`

```json
{
	"configurations": [
		{
			"name": "ZMS5-DEV",
			"type": "python",
			"request": "launch",
			"program": "~/vpy37/bin/runwsgi",
			"justMyCode": false,
			"console": "integratedTerminal",
			"args": [
				"--debug",
				"--verbose",
				"~/instance/zms5_dev/etc/zope.ini",
				"debug-mode=on",
				// "http_port=8086",
			],
			"env": {
				"PYTHONUNBUFFERED":"1",
				"CONFIG_FILE": "~/instance/zms5_dev/etc/zope.ini",
				"INSTANCE_HOME": "~/instance/zms5_dev",
				"CLIENT_HOME": "~/instance/zms5_dev",
				"PYTHON": "~/vpy37/bin/python",
				"SOFTWARE_HOME": "~/vpy37/bin/"
			},
		},
	]
}
```
If the paths in launch config correspond to the ones of your development machine you can start Zope with the Python debugger via the configuration item *Python3: Zope-ZMS5* in the debug menu of VS Code. The Zope server can be addressed in a web browser via `http://localhost:8080`. The environment will look like this:

![Install VS Code](images/develop_vscode_setup.png)

<br />

## <a id="git_connections"></a>Git Connection
Visual Studio Code has git support built in, so you do not need a further extension. The main Git features are:
+ initialize / clone a repository.
+ create branches and tags
+ stage and commit changes.
+ push/pull/sync with a remote branch.
+ resolve merge conflicts.
+ view diffs


The prerequisites for using Git are 
1. Git needs to be installed on the system (on Windows it is easier to use Git via WSL)
2. Public keys of the Git domains should be saved in the `~/.ssh/known_hosts` file
3. Private keys (if used for ssh connection) should be referenced in `~/.ssh/config` like this

```txt
host github.com
	HostName github.com
	# Port 443
	IdentityFile ~/.ssh/myname_openssh.ppk
	User myname
```

Useful Links:
+ [On Ubuntu VS Code gives me an ssh_askpass error when I try to push the changes to my Github repository](https://stackoverflow.com/questions/52885928/vs-code-gives-me-an-ssh-askpass-error-when-i-try-to-push-the-changes-to-my-githu#52886041)

+ [How to use Git credential store on Windows Sublinux, WSL?]( https://stackoverflow.com/questions/45925964/how-to-use-git-credential-store-on-wsl-ubuntu-on-windows)

+ [VS Code extension for managing pull requests and issues on Github](https://marketplace.visualstudio.com/items?itemName=GitHub.vscode-pull-request-github)


## Remote Development
The [Remote Development Extension Pack](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack) allows you to open a remote folder on any remote machine, virtual machine, or container with a running SSH server and take full advantage of VS Code's feature set.
After getting connected to the remote server VS Code installs a Node.js Express web app that allows editing and debugging on the remote machine just like if the source code was local.

Useful Links:
+ [VS Code Remote Development](https://code.visualstudio.com/docs/remote/remote-overview)
+ [Remote development over SSH](https://code.visualstudio.com/docs/remote/ssh-tutorial)

The remote explorer menu allows to add your server connections; VS code refers to the user's existing ssh connection by reading the local `~/.ssh/config` file (*see* [git connections](#git_connections)).

![Remote Explorer Menu](images/develop_vscode_remote0.png)

Usually you should connect with the **username that is used for running Zope** so that you can run it controlled by VS Code. 
Example config:
```
Host 192.168.48.15
	HostName 192.168.48.15
	User zope
	ForwardAgent yes
```
The next screen images shows a remote connection from VS Code (Win10) to a Ubuntu-VM. After the first connection VS Code installs some Node.js server files into the  remote machine's folder `~/.vscode-server`. 

![Remote Connection](images/develop_vscode_remote1.png)

Then you can open folders on the remote machine and save them as a VS Code *workspace*. This happens to the remote folder `~/.vscode`. 

![Start Debugging](images/develop_vscode_remote2.png)


## Debugging in a ZEO environment
In an [ZEO environment](https://zope.readthedocs.io/en/latest/zopebook/ZEO.html#what-is-zeo) VS Code can launch one more Zope instance in parallel to the running ZEO clients. The launch script needs an additional argument for a separate HTTP port (e.g. `http_port=8088`) the launched instance should communicate with. VS Code recognizes all the ports that are served by ZEO clients and shows it in the remote explorer menu. You can click on the browser button to address this port via port forewarding on localhost for viewing the just started debugging instance:

![Debugging in a ZEO environment](images/develop_vscode_remote3.png)
*After launching the Zope debugging instance by VS Code the remote explorer menu automatically shows all ports the ZEO environment is communicating with (left side, bottom). A click on a browser icon starts a new browser windows requesting that port via VS Code controlled forwording*

### launch.config
*Important hint*: Please, set the `http_port` argument to run the Zope instance for debugging on a vacant port:

```json
{
	"configurations": [

		{
			"name": "ZMS5-DEV",
			"type": "python",
			"request": "launch",
			"program": "~/vpy37/bin/runwsgi",
			"justMyCode": false,
			"console": "integratedTerminal",
			"args": [
				"--debug",
				"--verbose",
				"~/instance/zms5_dev/etc/zope.ini",
				"debug-mode=on",
				"http_port=8086",
			],
			"env": {
				"PYTHONUNBUFFERED":"1",
				"CONFIG_FILE": "~/instance/zms5_dev/etc/zope.ini",
				"INSTANCE_HOME": "~/instance/zms5_dev",
				"CLIENT_HOME": "~/instance/zms5_dev",
				"PYTHON": "~/vpy37/bin/python",
				"SOFTWARE_HOME": "~/vpy37/bin/"
			},
		},
	]
}
```
*After setting up  VS Code to launch the remote Zope in debug-mode you can interfere with Zope/ZMS code on the remote machine:*
![Debugging in a ZEO environment](images/develop_vscode_remote4.png)


### Configuring HTTP Port Number as a Script Argument
Usually ZEO starts one installed Zope instance multiple times on several ports and thus runs them in different processes in parallel.
To manage that Zope's ini-file `$instance_dir/etc/zope.ini` gets the http-port as a variable `%(http_port)s`:

```
[app:zope]
use = egg:Zope#main
zope_conf = %(here)s/zope.conf

[server:main]
use = egg:waitress#main
host = 127.0.0.1
# port = 8080
port = %(http_port)s

```

Now the upper launch script will start Zope on that port which is given as an argument.

## Configuring Zope for the Use of ZEO

The `zope.conf` needs some changes of the database section for accessing the ZODB via ZEO as client:

```xml
%define INSTANCE /home/zope/instances/zms5

instancehome $INSTANCE
trusted-proxy 127.0.0.1

%import ZEO

<zodb_db main>
    <clientstorage>
        server $INSTANCE/var/zeosocket
        storage main
        name zeostorage Data.fs
        client-label zms5_zeo 8080
    </clientstorage>
    mount-point /
</zodb_db>
```


An additional file `zeo.conf` sets the application's socket file:

```xml
%define INSTANCE /home/zope/instances/zms5

<zeo>
    address $INSTANCE/var/zeosocket
</zeo>

<filestorage main>
    path $INSTANCE/var/Data.fs
</filestorage>
```
As an example the following shell scripts starts ZEO first and then the Zope instance two times on different ports: 


```sh
#!/bin/bash

instance_dir="/home/zope/instances/zms5_dev"
venv_bin_dir="/home/zope/vpy38/bin"

nohup  $venv_bin_dir/runzeo --configure $instance_dir/etc/zeo.conf 1>/dev/null 2>/dev/null &
echo "ZEO started"
nohup  $venv_bin_dir/runwsgi --debug --verbose $instance_dir/etc/zope.ini debug-mode=on http_port=8085 1>/dev/null 2>/dev/null &
echo "ZOPE 8085 started"
nohup $venv_bin_dir/runwsgi --debug --verbose $instance_dir/etc/zope.ini debug-mode=on http_port=8086 1>/dev/null 2>/dev/null &
echo "ZOPE 8086 started"
```


More details  about the ZEO configuration are described in the <a href="https://zeo.readthedocs.io/en/latest/clients.html#configuration-strings-files">ZEO docs</a> 



## WebDAV-Editing of Zope Objects

**Important Note**: _WebDAV should only be used in a safe (development) environment with localhost and/or SSL port-forwarding._

Since Zope's new default web server (<a href="https://zope.readthedocs.io/en/latest/news.html?highlight=ftp#wsgi-as-the-new-default-server-type">WSGI</a>) does not provide ftp communication, the WebDAV protocol can be used for Zope object editing. Zope's WebDAV interface is configured in two steps:

1. Add a new line to  Zope config-file `./etc/zope.conf` to enable the WebDAV feature:
	```
	webdav-source-port 8091
	```

2. Add a new address to the default Zope WSGI server config-file `./etc/zope.ini`. The new address for the WebDAV connection `127.0.0.1:8091` will be added by the argument `listen`, which allows multiple host/port combinations. _Hint: arguments `host` and `port` must not be used, if `listen` is used._
	```
	[server:main]
	use = egg:waitress#main
	# host = 127.0.0.1
	# port = 8080
	listen = 127.0.0.1:8080 127.0.0.1:8091 
	```
	If the server should accept webdav request from any server-ip the argument `listen` can even use wildcards. _Hint: Be careful with wildcards; for security reasons an exosed system should use the restriction to localhost and for access key-based access with port forwarding should be preferred in general._
	```
	listen = 127.0.0.1:8080 *:8091 
	```



After restarting the Zope instance WebDAV protocol will be available. 
To make VSCode work with WebDAV a special plugin is needed: "Remote Workspace" can be installed via VSCode Marketplace

https://marketplace.visualstudio.com/items?itemName=Liveecommerce.vscode-remote-workspace

To show Zope's object tree as an editable file tree,  VSCode's _code-workspace_ file needs a new entry to establish the WebDAV connections:

```json
{
	"name": "Zope-WebDAV Access",
	"uri": "webdav://admin:****@localhost:8091/"
}
```
Now the  WebDAV file tree apears in the VSCode Explorer view, can be naviagated and nodes can be edited.

![Debugging in a ZEO environment](images/develop_vscode_webdav.gif)
_WebDAV editing of Zope objects: the left screen shows the browser based ZMI and the right screen shows the VSCode editor view of the Zope document tree and the same Python Script object_
