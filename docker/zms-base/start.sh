#!/bin/bash
# The ZEO/Zope start script works in two steps:
# 1. ZEO server is started silently (nohub)
# 2. Zope instance it started on parameter defined port:8085
# Sending Zope's output not to dev/null but the console maintains
# docker running

instance_dir="/home/zope/instance/"
venv_bin_dir="/home/zope/venv/bin"

# echo "Step-1: Starting ZEO"
# nohup  $venv_bin_dir/runzeo --configure $instance_dir/etc/zeo.conf 1>/dev/null 2>/dev/null &

echo "Step-2: Starting ZOPE 80"
# FIXME does this need --debug, and what do I do to get rid of it in production?
$venv_bin_dir/runwsgi --debug --verbose $instance_dir/etc/zope.ini debug-mode=on http_port=80


