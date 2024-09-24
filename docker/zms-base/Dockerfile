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

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
ENV UV_LINK_MODE=copy

# Create venv and permanently enable it
# ARG CREATE_VENV_COMMAND="uv venv"
ARG CREATE_VENV_COMMAND="python3 -m venv"
ENV VIRTUAL_ENV=/home/zope/venv
RUN $CREATE_VENV_COMMAND $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Enable caching of pip packages to speed up rebuild times
# cannot use uv as long as so many editable packages need to be installed
# ARG PIP_INSTALL="uv pip install"
ARG PIP_INSTALL="pip install --config-settings editable_mode=compat"
ENV PIP_CACHE_DIR=/home/zope/venv/cache
RUN --mount=type=cache,uid=$UID,target=$PIP_CACHE_DIR,sharing=locked <<EOR
    set -ex

    if echo ${PIP_INSTALL} | grep -qv "\buv\b"; then
        $PIP_INSTALL --cache-dir $PIP_CACHE_DIR --upgrade pip wheel setuptools
    fi
    $PIP_INSTALL --cache-dir $PIP_CACHE_DIR --upgrade --editable git+https://github.com/zms-publishing/ZMS.git#egg=ZMS
    $PIP_INSTALL --cache-dir $PIP_CACHE_DIR --requirement https://raw.githubusercontent.com/zms-publishing/ZMS5/master/requirements-full.txt
    $PIP_INSTALL --cache-dir $PIP_CACHE_DIR --upgrade --editable git+https://github.com/sntl-projects/Products.zmsPluggableAuthService.git#egg=Products.zmsPluggableAuthService[nginx-sso]
    $PIP_INSTALL --cache-dir $PIP_CACHE_DIR ZEO
    $PIP_INSTALL --cache-dir $PIP_CACHE_DIR debugpy
EOR

# TODO install debugging helpers like: pip install debugpy

# Create Zope Instance
RUN mkwsgiinstance --dir instance --user admin:admin

# Configure Zope Instance
COPY --chown=zope:zope --chmod=500 start.sh instance/bin/start.sh
COPY --chown=zope:zope zope.ini instance/etc/zope.ini
COPY --chown=zope:zope zope.conf instance/etc/zope.conf

# COPY --chown=zope:zope ./etc instance/etc
# COPY ./var venv/instance/zms5/var
# COPY ./Extensions venv/instance/zms5/Extensions

CMD ["/home/zope/instance/bin/start.sh"]
