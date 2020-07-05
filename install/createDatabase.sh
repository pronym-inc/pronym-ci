#!/usr/bin/env bash
echo "Creating database..."
createuser -s pronym_ci || :
createdb -O pronym_ci pronym_ci || :