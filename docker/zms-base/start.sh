#!/bin/bash
instance_dir="/home/zope/instance/"
venv_bin_dir="/home/zope/venv/bin"

# Regarding debug-mode=on
# @see https://zope.readthedocs.io/en/latest/zopebook/InstallingZope.html#the-debug-mode-directive
# recommend to disable debug-mode in production as it auto reloads templates on change
# @see https://zope.readthedocs.io/en/latest/zdgbook/TestingAndDebugging.html#debug-mode
# mentions that this also shows backtraces to users
# @see https://zope.readthedocs.io/en/latest/news.html#wsgi-as-the-new-default-server-type
# mentions that this disables a httpexceptions midleware and shows backtraces on the console>
# TODO talk to FH if this makes sense. Might require a slightly different workflow from them.
# Currently always enabled on our servers.

# Regarding --debug
# @see https://zope.readthedocs.io/en/latest/operation.html#running-zope-in-the-foreground
# seems to sugges that this also enables the debug-mode directive
# TODO talk to FH to allow me to check that

exec $venv_bin_dir/runwsgi --debug --verbose $instance_dir/etc/zope.ini debug-mode=on http_port=80
