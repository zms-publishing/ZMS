#!/bin/bash
# The ZEO/Zope start script works in two steps:
# 1. ZEO server is started silently (nohub)
# 2. Zope instances are started on port:8085/8086
# HINTS: The ZEO server is started in the background 
# and the script waits for it to be ready before starting the Zope instances.
# The Zope instances are started in the background and the script waits for them to be ready before proceeding.

instance_dir="/home/zope"
venv_bin_dir="/home/zope/venv/bin"

echo "Step-1: Starting ZEO"
nohup  $venv_bin_dir/runzeo --configure $instance_dir/etc/zeo.conf 1>/dev/null 2>/dev/null &

echo "Step-2: Starting ZOPE 8085"
nohup $venv_bin_dir/runwsgi --debug --verbose $instance_dir/etc/zope.ini debug-mode=on http_port=8085 1>/dev/null 2>/dev/null &
while ! echo > /dev/tcp/127.0.0.1/8085; do
  echo "Waiting for Zope to start on port 8085 .."
  sleep 1
done
echo "Zope started on port 8085"

echo "Step-3: Starting ZOPE 8086"
nohup $venv_bin_dir/runwsgi --debug --verbose $instance_dir/etc/zope.ini debug-mode=on http_port=8086 1>/dev/null 2>/dev/null &
while ! echo > /dev/tcp/127.0.0.1/8086; do
  echo "Waiting for Zope to start on port 8086 .."
  sleep 1
done
echo "Zope started on port 8086"

