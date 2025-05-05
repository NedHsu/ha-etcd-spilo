#!/bin/bash

# Replace environment variables in servers.json
envsubst < /pgadmin4/servers.json > /tmp/servers.json
mv /tmp/servers.json /pgadmin4/servers.json

# Start pgAdmin
/entrypoint.sh 