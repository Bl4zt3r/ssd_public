#!/bin/sh
set -e

: "${SERVER_ADDR:?SERVER_ADDR not set}"

host=$(echo "$SERVER_ADDR" | sed -E 's#https?://([^/]+)/?.*#\1#')

echo "Waiting for server $host..."
until ping -c1 -W1 "$host" >/dev/null 2>&1; do
  sleep 2
done

exec python sensor_simulator.py
