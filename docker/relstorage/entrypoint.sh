#!/bin/bash

# Wait for PostgreSQL to be ready (important for container orchestration)
echo "Waiting for PostgreSQL..."
while ! pg_isready -h postgres; do
  sleep 2
done
echo "PostgreSQL is ready!"

# # Create the database if it doesn't exist
# echo "Creating database..."
# psql -c "CREATE USER zope WITH PASSWORD 'zope';"
# psql -c "CREATE DATABASE zodb OWNER zope;"

# Start Zope
echo "Starting Zope..."
/home/zope/venv/bin/runwsgi -v /home/zope/etc/zope.ini

# Let the container run: Start Zope with VScode-Debugger
# tail -f /dev/null

