#!/bin/bash

mkdir -v data/prod
chown :django data/prod
chmod 775 data/prod
chmod g+s data/prod
