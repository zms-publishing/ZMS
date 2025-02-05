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
    apt --yes install libldap2-dev libsasl2-dev git
EOR

# Drop root privileges
ENV UID=1000
ENV GID=1000
RUN groupadd --gid $GID zope ; useradd --system --create-home --uid $UID --gid $GID zope
USER zope
WORKDIR /home/zope/

# Install uv
# COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
# ENV UV_LINK_MODE=copy

# Create venv and permanently enable it
# ARG CREATE_VENV_COMMAND="uv venv"
ARG CREATE_VENV_COMMAND="python3 -m venv"
ENV VIRTUAL_ENV=/home/zope/venv
RUN $CREATE_VENV_COMMAND $VIRTUAL_ENV
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
COPY --chown=zope:zope requirements*.txt setup.py setup.cfg README.rst ./

ENV PIP_CACHE_DIR=/home/zope/venv/cache
RUN --mount=type=cache,uid=$UID,target=$PIP_CACHE_DIR,sharing=locked <<EOR
    set -ex

    if echo ${PIP_INSTALL} | grep -qv "\buv\b"; then
        $PIP_INSTALL --cache-dir $PIP_CACHE_DIR --upgrade pip wheel setuptools
    fi
    $PIP_INSTALL --cache-dir $PIP_CACHE_DIR --editable .[dev]
    $PIP_INSTALL --cache-dir $PIP_CACHE_DIR --requirement requirements-full.txt
    $PIP_INSTALL --cache-dir $PIP_CACHE_DIR --upgrade git+https://github.com/sntl-projects/Products.zmsPluggableAuthService.git#egg=Products.zmsPluggableAuthService[nginx-sso]
    $PIP_INSTALL --cache-dir $PIP_CACHE_DIR ZEO
EOR

# Create Zope Instance
RUN mkwsgiinstance --dir . --user admin:admin

# Configure Zope Instance
ARG BUILD_DIR=docker/base
COPY --chown=zope:zope $BUILD_DIR/zope.ini etc/zope.ini
COPY --chown=zope:zope $BUILD_DIR/zope.conf etc/zope.conf
COPY --chown=zope:zope $BUILD_DIR/zeo.conf etc/zeo.conf
RUN mkdir cache Extensions

COPY --chown=zope:zope Products Products
# consider if we need the test code to be in the container to run
# in github actions or similar circumstances
# locally it is mapped into the container via bindmounts
# COPY --chown=zope:zope selenium_tests test_output tests ./

CMD ["runwsgi", "--verbose", "etc/zope.ini", "http_port=80"]
