#!/bin/sh
set -e

for var in POSTGRES_HOST POSTGRES_DB POSTGRES_USER POSTGRES_PASSWORD; do
  eval val=\"\$$var\"
  if [ -z "$val" ]; then
    echo "Missing env var: $var" >&2
    exit 1
  fi
done

echo "Waiting for database $POSTGRES_HOST..."
until ping -c1 -W1 "$POSTGRES_HOST" >/dev/null 2>&1; do
  sleep 2
done

exec python main.py
