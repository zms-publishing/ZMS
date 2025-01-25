#!/bin/bash
# The starting script works in three steps:
# 1. ZEO server in background (nohub)
# 2. Zope instance in background (nohub)
# 3. VSCode-Server maintains docker running

instance_dir="/home/zope"
venv_bin_dir="/home/zope/venv/bin"
zope_port="8085"
vscode_port="8080"

echo "Step-1: Starting ZEO"
nohup $venv_bin_dir/runzeo --configure $instance_dir/etc/zeo.conf 1>/dev/null 2>/dev/null &

echo "Step-2: Starting ZOPE on port $zope_port"
#\* $venv_bin_dir/runwsgi --debug --verbose $instance_dir/etc/zope.ini debug-mode=on http_port=8085
nohup $venv_bin_dir/runwsgi --debug --verbose $instance_dir/etc/zope.ini debug-mode=on http_port=$zope_port 1>/dev/null 2>/dev/null &

echo "Start VSCode-Server on port $vscode_port"
code-server --bind-addr 0.0.0.0:$vscode_port --auth none  $instance_dir

#\* 
# HINT: If Step-2 is final Zope's output shall not sent to dev/null 
# but the console for maintaining docker running

