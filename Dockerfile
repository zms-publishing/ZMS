FROM ep-devops.id.unibe.ch:5000/id/unibe-cms-base:python3.11.1-zope5.8

COPY backend/zms-core/requirements-unibe.txt $APPHOME/requirements-unibe.txt
COPY backend/zms-sso-plugin $APPHOME/sso-plugin

# Workaround to avoid Rust/cargo dependency of cryptography requirement by Products.zmsPluggableAuthService
# which causes version mismatch with python3.6.9 and extrem long running builds with python 3.9.x
# see https://github.com/docker/compose/issues/8105
# see https://cryptography.io/en/latest/installation/#alpine
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

RUN apk update \
 && apk --no-cache add \
    freetype-dev \
    jpeg-dev \
    lcms2-dev \
    libxml2-dev \
    libxslt-dev \
    mariadb-dev \
    openjpeg-dev \
    openldap-dev \
    tiff-dev \
    tk-dev \
    tcl-dev \
    zlib-dev \
 && rm -rf /tmp/* /var/cache/apk/* /var/tmp/* \
 && $APPHOME/bin/pip install $APPHOME/sso-plugin[nginx-sso] \
    -r $APPHOME/requirements-unibe.txt \
    -c https://zopefoundation.github.io/Zope/releases/5.8/constraints.txt

COPY backend/zms-core $APPHOME/zms-core

RUN $APPHOME/bin/pip install $APPHOME/zms-core \
    -c https://zopefoundation.github.io/Zope/releases/5.8/constraints.txt \
 && $APPHOME/bin/mkwsgiinstance -d $APPHOME -u admin:admin

# TODO src vs. dist => gulp automation...?!
COPY frontend/web/estatico-handlebars/src/assets $APPHOME/frontend/web/estatico-handlebars/src/assets
# TODO app vs. ?!? => mount host directory for shared access in cluster
COPY frontend/zms/models $APPHOME/zms/models

COPY conf $APPHOME/conf
COPY init_scripts $ENTRYPOINT_SCRIPTS