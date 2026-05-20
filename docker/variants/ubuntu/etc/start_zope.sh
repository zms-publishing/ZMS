#!/bin/bash

# -----------------------------------------------------------------
# The script starts a Zope instance in a container
# It needs two environment variables:
# - HTTP_PORT: The port on which the host will listen to Zope
# - READ_ONLY: The read-only flag for the Zope instance
# -----------------------------------------------------------------


# Check if required environment variables are set
if [ -z "$HTTP_PORT" ]; then
  echo "Error: HTTP_PORT is not set."
  exit 1
else
  echo "HTTP_PORT is set to $HTTP_PORT"
fi
if [ -z "$READ_ONLY" ]; then
  echo "Error: READ_ONLY is not set."
  exit 1
else
  echo "READ_ONLY is set to $READ_ONLY"
fi

INSTANCE_DIR="/home/zope"
VENV_DIR="/home/zope/venv"

# Set up environment
export PATH="${VENV_DIR}/bin:$PATH"

# Set a timestamp for the conf file creation
export CONF_TS=$(date +"%Y%m%d_%H%M%S")

# ---------------------------------
# Start Zope instance
# with a dynamically generated zope.conf 
# ---------------------------------
# Create zope.conf for given HTTP_PORT
envsubst '$HTTP_PORT $READ_ONLY $CONF_TS' < "${INSTANCE_DIR}/etc/zope.conf.tmpl" > "${INSTANCE_DIR}/etc/zope_$HTTP_PORT.conf"

# Wait until the conf file was created successfully
while [ ! -f "${INSTANCE_DIR}/etc/zope_$HTTP_PORT.conf" ]; do
  echo "Waiting for zope.conf to be created ..."
  sleep 1
done

# Wait for ZEO server to start by monitoring its log file
echo "Waiting for ZEO server to start listening on socket..."
max_wait=60  # Maximum seconds to wait
elapsed=0
while ! tail -n 20 "${INSTANCE_DIR}/var/log/zeo.log" 2>/dev/null | grep -q "listening on"; do
  echo "Waiting for ZEO server to start... ($elapsed seconds)"
  sleep 1
  elapsed=$((elapsed+1))
  # Check if maximum waiting time is exceeded
  if [ $elapsed -ge $max_wait ]; then
    echo "ERROR: Timed out waiting for ZEO server to start (${max_wait}s)"
    exit 1
  fi
done
echo "ZEO server is now listening on socket"

# Start Zope instance
echo "Starting Zope instance ..."
nohup $VENV_DIR/bin/runwsgi  --debug --verbose $INSTANCE_DIR/etc/zope.ini debug-mode=on http_port=$HTTP_PORT 1>/dev/null 2>/dev/null &
while ! nc -z localhost 8080; do
  echo "Waiting for Zope to start ..."
  sleep 1
done
sleep 2
echo "Zope started on port 8080 and publishing on $HTTP_PORT"
# ---------------------------------
