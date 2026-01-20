ARG BUILD_PYTHON_VERSION=3.12
FROM python:$BUILD_PYTHON_VERSION
ARG BUILD_PYTHON_VERSION

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
    apt --yes install libldap2-dev libsasl2-dev git
EOR

# Drop root privileges
# We need hardcoded uid/gid so we can later share the production files as bind mounts with the correct uid/gid
ENV UID=1000
ENV GID=1000
RUN groupadd --gid $GID zope ; useradd --system --create-home --uid $UID --gid $GID zope
USER zope
WORKDIR /home/zope/

# Configure git for user
RUN <<EOR
    git config --global user.email "zmsbot@container"
    git config --global user.name "zmsbot"
EOR

# Provide ZEO health check script
COPY --chown=zope:zope docker/base/zeo_health_check.py /home/zope/bin/zeo_health_check.py

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
ENV UV_LINK_MODE=copy
# vastly improve startup time https://docs.astral.sh/uv/guides/integration/docker/#compiling-bytecode
ENV UV_COMPILE_BYTECODE=1

# Create venv and permanently enable it
ARG CREATE_VENV_COMMAND="uv venv"
# ARG CREATE_VENV_COMMAND="python3 -m venv"
ENV VIRTUAL_ENV=/home/zope/venv
RUN <<EOR
    $CREATE_VENV_COMMAND $VIRTUAL_ENV
    ln -s ${VIRTUAL_ENV}/lib/python$BUILD_PYTHON_VERSION/site-packages/ ${VIRTUAL_ENV}/site-packages
EOR
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Local builds greatly accelerate, if we do not need to download all pip packages from scratch every time
ENV PIP_CACHE_DIR=/home/zope/venv/cache
# ENV PIP_CACHE_DIR=/home/zope/.cache/uv
#
# Enable caching of pip packages to speed up rebuild times
# uv also cannot install editable eggs from git repos, but I think we don't need that
ARG PIP_INSTALL="uv pip install --cache-dir $PIP_CACHE_DIR"
# may need to switch back to pip if the pyproject.toml requirement kicks in
# ARG PIP_INSTALL="pip install --config-settings editable_mode=compat --cache-dir $PIP_CACHE_DIR"

# Only install dependenies now, to maximize layer caching
COPY --chown=zope:zope pyproject.toml requirements*.txt ./
RUN --mount=type=cache,uid=$UID,target=$PIP_CACHE_DIR,sharing=locked <<EOR
    set -ex

    if echo ${PIP_INSTALL} | grep -qv "\buv\b"; then
        $PIP_INSTALL --upgrade pip wheel setuptools
    fi
    $PIP_INSTALL --requirement requirements-full.txt
    $PIP_INSTALL --requirement pyproject.toml
    $PIP_INSTALL --upgrade git+https://github.com/sntl-projects/Products.zmsPluggableAuthService.git#egg=Products.zmsPluggableAuthService[nginx-sso]
    $PIP_INSTALL ZEO
EOR

# Create Zope Instance
# We do this, to make it easy to evaluate zms without having to create an initial zodb outside the container and map it inside.
# However: mkwsgiinstance creates a file inituser in the top level of the deployment
# This file is read on the first startup of zope, and creates the actual initial user in the zodb
# consuming that file. Therefore we must be very cautious to ensuret that this file itself is _not_
# part of the docker image. zconsole triggers that same startup behaviour.
RUN <<EOR
    mkdir cache Extensions customizing import
    mkwsgiinstance --dir . --user admin:admin
    echo | zconsole debug etc/zope.conf
EOR

# Configure Zope Instance
ARG BUILD_DIR=docker/base
COPY --chown=zope:zope $BUILD_DIR/zope.ini etc/zope.ini
COPY --chown=zope:zope $BUILD_DIR/zope.conf etc/zope.conf
COPY --chown=zope:zope $BUILD_DIR/zeo.conf etc/zeo.conf

# Copy in and install zms last, to maximize layer caching
COPY --chown=zope:zope requirements*.txt pyproject.toml setup.cfg README.rst ./
COPY --chown=zope:zope src src
RUN --mount=type=cache,uid=$UID,target=$PIP_CACHE_DIR,sharing=locked <<EOR
    set -ex
    $PIP_INSTALL --editable .[dev]
EOR

# consider if we need the test code to be in the container to run
# in github actions or similar circumstances
# locally it is mapped into the container via bindmounts
# COPY --chown=zope:zope selenium_tests test_output tests ./

CMD ["runwsgi", "--verbose", "etc/zope.ini", "http_port=80"]
