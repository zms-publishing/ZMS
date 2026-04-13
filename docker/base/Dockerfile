ARG BUILD_PYTHON_VERSION=3.14
FROM python:$BUILD_PYTHON_VERSION
ARG BUILD_PYTHON_VERSION

EXPOSE 80

ARG CI_COMMIT_SHA=development
ENV CI_COMMIT_SHA=$CI_COMMIT_SHA

# Ensure all system packages are up to date
ENV DEBIAN_FRONTEND=noninteractive
RUN <<EOR
    set -eux
    sed -i 's/^Components: main$/Components: main contrib non-free non-free-firmware/' /etc/apt/sources.list.d/debian.sources
EOR

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
    set -eux
    echo "ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true" | debconf-set-selections
    apt update
    apt --yes install \
        docbook-xml \
        docbook-xsl \
        fop \
        git \
        libfop-java \
        libldap2-dev \
        libsasl2-dev \
        libxalan2-java \
        ttf-mscorefonts-installer \
        xalan \
        xsltproc
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
COPY --chown=zope:zope docker/base/zeo_health_check.py bin/zeo_health_check.py
# generic run script
COPY --chown=zope:zope docker/base/run-zope.sh bin/run-zope.sh

# Install uv
# COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
# ENV UV_LINK_MODE=copy

# Create venv and permanently enable it
# ARG CREATE_VENV_COMMAND="uv venv"
ARG CREATE_VENV_COMMAND="python3 -m venv"
ENV VIRTUAL_ENV=/home/zope/venv
RUN <<EOR
    $CREATE_VENV_COMMAND $VIRTUAL_ENV
    ln -s ${VIRTUAL_ENV}/lib/python$BUILD_PYTHON_VERSION/site-packages/ ${VIRTUAL_ENV}/site-packages
EOR
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Enable caching of pip packages to speed up rebuild times
# uv follows the new editable spec, even if the package (zms) does not provide a pyproject.toml
# this creates entries like __editable__.ZMS-5.2.0.finder.__path_hook__ in `Products.__path__`
# which Zope cannot handle yet
# @see https://github.com/zopefoundation/Zope/issues/1239
# uv also cannot install editable eggs from git repos, but I think we don't need that
# ARG PIP_INSTALL="uv pip install"
# may need to switch back to pip if the pyproject.toml requirement kicks in
ARG PIP_INSTALL="pip install --config-settings editable_mode=compat"

COPY --chown=zope:zope Products/zms/version.txt Products/zms/version.txt
COPY --chown=zope:zope requirements*.txt pyproject.toml README.rst ./
COPY --chown=zope:zope Products Products

ENV PIP_CACHE_DIR=/home/zope/venv/cache
RUN --mount=type=cache,uid=$UID,target=$PIP_CACHE_DIR,sharing=locked <<EOR
    set -ex

    if echo ${PIP_INSTALL} | grep -qv "\buv\b"; then
        $PIP_INSTALL --cache-dir $PIP_CACHE_DIR --upgrade pip wheel setuptools
    fi
    $PIP_INSTALL --cache-dir $PIP_CACHE_DIR --editable .[dev]
    $PIP_INSTALL --cache-dir $PIP_CACHE_DIR --requirement requirements-full.txt
    $PIP_INSTALL --cache-dir $PIP_CACHE_DIR --upgrade 'Products.zmsPluggableAuthService[nginx-sso] @ git+https://github.com/sntl-projects/Products.zmsPluggableAuthService.git'
    $PIP_INSTALL --cache-dir $PIP_CACHE_DIR ZEO
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

# consider if we need the test code to be in the container to run
# in github actions or similar circumstances
# locally it is mapped into the container via bindmounts
# COPY --chown=zope:zope selenium_tests test_output tests ./

ENV HTTP_PORT=${HTTP_PORT:-80}
CMD ["bin/run-zope.sh"]
CMD ["runwsgi", "--verbose", "etc/zope.ini", "http_port=80"]
