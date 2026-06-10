# A. Getting Started

This chapter guides you through installing ZMS from scratch, creating your first Zope instance, and logging in to the ZMS Management Interface for the first time.

> **See also:** [develop_intro_en.md](develop_intro_en.md) for the full developer-oriented installation walkthrough.

---

## Prerequisites

The following setup has been tested on Ubuntu 24.04 and works similarly on other Unix-like systems (including Windows Subsystem for Linux, WSL). It is recommended to create a dedicated non-root user (e.g. `zope`) to run the Zope application server.

ZMS requires **Python 3.10 or later**. Check your installed version:

```console
~$ python3 --version
```

Update or reinstall Python 3 if it is missing or outdated.

ZMS runs on **Zope 5+** as its underlying application server. Install the required OS packages first:

```console
~$ sudo apt-get update && sudo apt-get -y upgrade
~$ sudo apt-get install -y ca-certificates && sudo update-ca-certificates
~$ sudo apt-get install -y locales locales-all
~$ sudo apt-get install -y make gcc g++ git build-essential
~$ sudo apt-get install -y python3 python3-dev python3-venv
~$ sudo apt-get install -y default-libmysqlclient-dev build-essential pkg-config
~$ sudo apt-get install -y slapd libldap2-dev libsasl2-dev
~$ sudo apt-get install -y memcached
```

---

## 1. Set up a virtual Python environment

Create a dedicated user and a virtual environment to keep the ZMS installation isolated:

```console
~$ adduser zope && usermod -aG sudo zope
~$ su - zope
~$ python3 -m venv /home/zope/vpy3
```

---

## 2. Install ZMS

Activate the virtual environment and install ZMS from GitHub using `pip`:

```console
~$ cd /home/zope/vpy3/bin/
~$ source activate
~$ ./pip install -U pip wheel setuptools
~$ ./pip install -r https://raw.githubusercontent.com/zms-publishing/ZMS/main/requirements-full.txt
~$ ./pip install --use-pep517 --config-settings editable_mode=compat \
       -e git+https://github.com/zms-publishing/ZMS.git@main#egg=Products.zms
~$ ./pip install ZEO
```

The `--editable` flag installs ZMS from source, which is recommended so you can update it with `git pull` later. Verify the installation:

```console
~$ ./pip list | grep -i zms
ZMS   6.0.0   /home/zope/src/ZMS
```

---

## 3. Create a Zope instance

Use the `mkwsgiinstance` command to scaffold a new Zope instance (here named `zms_dev`):

```console
~$ ./mkwsgiinstance -d /home/zope/instance/zms_dev
```

Follow the prompts to set the administrator username and password.

> More: <https://zope.readthedocs.io/en/latest/operation.html#creating-a-zope-instance>

---

## 4. Start the Zope server

```console
~$ ./runwsgi -v /home/zope/instance/zms_dev/etc/zope.ini
```

By default Zope listens on port **8080**. You can change the port in `zope.ini`.

> More: <https://zope.readthedocs.io/en/latest/operation.html#running-zope>

---

## 5. Add a ZMS node

Open your browser at `http://localhost:8080/manage` and log in with the administrator credentials you set in step 3.

1. Click **Add** in the Zope top bar.
2. Select **ZMS** from the list of available object types.
3. Fill in the ID, title, and initial language configuration.
4. Click **Add** to create the ZMS root node.

You will be redirected to the ZMS Management Interface (ZMI) showing the default content tree.

---

## 6. First steps in the ZMI

After logging in to ZMS you will see the **ZMS Management Interface**:

- The **top bar** contains meta functions (user profile, language switching, preview link).
- The **main menu** (tab row) switches between editing, properties, import/export, and other views.
- The **breadcrumb navigation** shows your position in the document tree.
- The **sitemap** (toggle in the top bar) provides a collapsible left-hand tree navigator.

Proceed to [B. For Editors](b_for_editors.md) to learn how to create your first content, or to [C. For Site Administrators](c_for_site_administrators.md) to configure the system for your organisation.

---

## Running ZMS as a system service

For production deployments it is common to run Zope/ZMS as a `systemd` service. A minimal unit file:

```ini
[Unit]
Description=ZMS / Zope Application Server
After=network.target

[Service]
Type=simple
User=zope
WorkingDirectory=/home/zope/vpy3/bin
ExecStart=/home/zope/vpy3/bin/runwsgi -v /home/zope/instance/zms_dev/etc/zope.ini
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Place the file at `/etc/systemd/system/zms.service`, then enable and start it:

```console
~$ sudo systemctl daemon-reload
~$ sudo systemctl enable zms
~$ sudo systemctl start zms
```

---

## Next steps

| Goal | Chapter |
|---|---|
| Create and edit content | [B. For Editors](b_for_editors.md) |
| Configure the site | [C. For Site Administrators](c_for_site_administrators.md) |
| Extend ZMS with code | [D. For Developers](d_for_developers.md) |
| Understand versioning and workflow | [E. Appendices](e_appendices.md) |
