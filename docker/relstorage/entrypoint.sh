#!/bin/bash

# Start PostgreSQL in the background
service postgresql start

# Wait for PostgreSQL to be ready
until pg_isready -U postgres; do
    echo "Waiting for PostgreSQL to start..."
    sleep 2
done

su -c "psql -c \"CREATE USER zodbuser WITH PASSWORD 'zodbuser';\"" postgres
su -c "psql -c \"CREATE DATABASE zodb OWNER zodbuser;\"" postgres

# Start Zope --> with VScode-Debugger
# su -c "runwsgi /home/zope/etc/zope.ini" zope

# Let the container run with zope
tail -f /dev/null

