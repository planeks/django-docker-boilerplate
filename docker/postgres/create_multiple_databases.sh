#!/bin/bash

set -e
set -u

function create_user_and_database() {
local database=$1
echo "Creating database '$database'"
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" << EOT
  CREATE DATABASE $database;
  GRANT ALL PRIVILEGES ON DATABASE $database TO $POSTGRES_USER;
EOT
}

if [ -n "$POSTGRES_ADDITIONAL_DATABASES" ]; then
  echo "Additional database creation requested; $POSTGRES_ADDITIONAL_DATABASES"
  for db in $(echo $POSTGRES_ADDITIONAL_DATABASES | tr ',' ' '); do
    create_user_and_database $db
  done
fi
