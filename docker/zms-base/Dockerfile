FROM python:3.12

EXPOSE 80

ARG CI_COMMIT_SHA=development
ENV CI_COMMIT_SHA=$CI_COMMIT_SHA

# Ensure all system packages are up to date
ENV DEBIAN_FRONTEND=noninteractive
RUN \
    --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    <<EOR
    apt update
    apt --yes upgrade
EOR

# Install Zope/ZEO Dependencies
RUN \
    --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    <<EOR
    apt update
    apt --yes install libldap2-dev libsasl2-dev
EOR

# Drop root privileges
ENV UID=1000
RUN useradd --system --create-home --uid $UID zope
USER zope:zope
WORKDIR /home/zope/

# Create venv and permanently enable it
ARG CREATE_VENV_COMMAND="python -m venv"
ENV VIRTUAL_ENV=/home/zope/venv
RUN $CREATE_VENV_COMMAND $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Enable caching of pip packages to speed up rebuild times
ENV PIP_CACHE_DIR=/home/zope/venv/cache
RUN --mount=type=cache,uid=$UID,target=$PIP_CACHE_DIR,sharing=locked <<EOR
    set -e
    pip install --cache-dir $PIP_CACHE_DIR --upgrade pip wheel setuptools
    pip install --cache-dir $PIP_CACHE_DIR --upgrade --editable git+https://github.com/zms-publishing/ZMS.git#egg=ZMS
    pip install --cache-dir $PIP_CACHE_DIR --requirement https://raw.githubusercontent.com/zms-publishing/ZMS5/master/requirements-full.txt
    pip install --cache-dir $PIP_CACHE_DIR --upgrade --editable -e git+https://github.com/sntl-projects/Products.zmsPluggableAuthService.git#egg=Products.zmsPluggableAuthService[nginx-sso]
    pip install --cache-dir $PIP_CACHE_DIR ZEO
    pip install --cache-dir $PIP_CACHE_DIR debugpy
EOR

# install debugging helpers like: pip install debugpy

# # Create Zope Instance
RUN mkwsgiinstance -d instance -u admin:admin

COPY --chown=zope:zope <<EOF instance/bin/start.sh
#!/bin/bash
instance_dir="/home/zope/instance/"
venv_bin_dir="/home/zope/venv/bin"
# FIXME does this need --debug, and what do I do to get rid of it in production?
$venv_bin_dir/runwsgi --debug --verbose $instance_dir/etc/zope.ini debug-mode=on http_port=80
EOF

# COPY --chown=zope:zope ./etc instance/etc
# COPY ./var venv/instance/zms5/var
# COPY ./Extensions venv/instance/zms5/Extensions

CMD ["/home/zope/instance/bin/start.sh"]
