ZMS: Simplified Content Modelling
=================================

ZMS is the Python-based Content Management and E-Publishing System for Science, Technology and Medicine. A simple editing interface and flexible content model (multilingualism, metadata, content objects, XML import/export, workflow etc.) is designed for optimal productivity for web sites, documentation and educational content. 

Modularity of the ZMS components and approved production processes turn ZMS into an incomparably rapid tool. The underlying efficiency-oriented publication model is the result of many consulting projects in recent years by HOFFMANN+LIEBENBERG in association with SNTL Publishing, Berlin.



Download
---------

* Source: https://github.com/zms-publishing/ZMS/
* Revisions: https://github.com/zms-publishing/ZMS/commits/master
* Archive: https://github.com/zms-publishing/ZMS/archive/master.zip

Installation (GNU/Linux, OSX/Darwin and Windows/WSL)
----------------------------------------------------

*NOTE*: See Prerequisites below.
    
**(1) Setup an Environment**
     
::

$ cd ~
$ python3 -m venv ~/ZMS
           
**(2) Install [or Upgrade] the Product**

::     

$ ./ZMS/bin/pip install https://github.com/zms-publishing/ZMS/archive/master.zip [--upgrade]

or install from pypi

::     

$ ./ZMS/bin/pip install ZMS [--upgrade]

**(3) Create an Instance [or restart on Upgrade]**

::     

$ ./ZMS/bin/mkwsgiinstance -d ../instance
$ ./ZMS/bin/runwsgi -v ../instance/etc/zope.ini

and finally "Add ZMS" via web user interface
http://localhost:8080/manage
(replace "localhost" with your system's IP address or domain name if no local installation)

More detailed instructions can be found here: https://github.com/zms-publishing/ZMS/blob/main/docs/develop_intro_en.md


Prerequisites
-------------

``virtualenv`` is the PyPA recommended tool for creating isolated Python environments:
https://virtualenv.pypa.io/en/latest/installation.html

``pip`` is the PyPA recommended tool for installing and managing Python packages:
https://pip.pypa.io/en/latest/installing.html

Users of Microsoft Windows 11 can enable the Windows subsystem for Linux (WSL) for installing ZMS as under Linux (`Bash on Ubuntu on Windows <https://msdn.microsoft.com/de-de/commandline/wsl/install_guide>`_). Apple OS X running updated Xcode command line tools causes compiler errors rather than warnings used until before. You can `downgrade these errors to warnings <https://langui.sh/2014/03/10/wunused-command-line-argument-hard-error-in-future-is-a-harsh-mistress/>`_ again. If you get compilation errors like ``fatal error: Python.h: No such file or directory compilation terminated``, install development headers using your system's recommended package manager.

____

Copyright (c) 2000-2025 `HOFFMANN+LIEBENBERG <http://www.hoffmannliebenberg.de>`_ in association with `SNTL Publishing <http://www.sntl-publishing.com>`_, Berlin. Code released under the `GNU General Public License v3 <http://www.gnu.org/licenses/gpl.html>`_ license.
