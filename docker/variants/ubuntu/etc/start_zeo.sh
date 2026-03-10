
#!/bin/bash
# -----------------------------------------------------------------
# The script starts a ZEO server in a container.
# The ZEO server is listening on a socket in the file system.
# -----------------------------------------------------------------

INSTANCE_DIR="/home/zope"
VENV_DIR="/home/zope/venv"

# Set up environment
export PATH="$VENV_DIR/bin:$PATH"

# ---------------------------------
# [A] Start ZEO server
# ---------------------------------

# Exit if socket exists and ZEO server is already running on it
if [ -S "$INSTANCE_DIR/var/zeosocket" ] && ss -xl | grep -q "$INSTANCE_DIR/var/zeosocket"; then
  echo "ZEO server already running on $INSTANCE_DIR/var/zeosocket"
  exit 0
fi

# Create Data.fs if file does not exist
# if ! [ -f "$INSTANCE_DIR/var/Data.fs" ]; then
#   echo "New Data.fs has to be created that ZEO can connect to."
#   $VENV_DIR/bin/python2 $INSTANCE_DIR/bin/create_zodb.py
#   sleep 2
# else
#   echo "Data.fs found."
# fi

echo "Starting ZEO server..."
nohup "$VENV_DIR/bin/runzeo" --configure "$INSTANCE_DIR/etc/zeo.conf" 1>/dev/null 2>/dev/null &

while ! ss -xl | grep -q "$INSTANCE_DIR/var/zeosocket"; do
  echo "ZEO-starting script is waiting for ZEO server to start..."
  sleep 1
done
echo "ZEO server has started on $INSTANCE_DIR/var/zeosocket"
# ---------------------------------
