#!/bin/bash

exec runwsgi --verbose etc/zope.ini http_port=$HTTP_PORT
