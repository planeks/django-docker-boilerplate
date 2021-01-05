#!/bin/bash

mkdir -v data/production_extras
chown :django data/production_extras
chmod 775 data/production_extras
chmod g+s data/production_extras

mkdir -v data/production_sessions
chown :django data/production_sessions
chmod 775 data/production_sessions
chmod g+s data/production_sessions

mkdir -v data/production_staticfiles
chown :django data/production_staticfiles
chmod 775 data/production_staticfiles
chmod g+s data/production_staticfiles
