#!/bin/sh
set -e

: "${CENTRAL_SERVER_URL:?CENTRAL_SERVER_URL not set}"

host=$(echo "$CENTRAL_SERVER_URL" | sed -E 's#https?://([^/]+)/?.*#\1#')

echo "Waiting for server $host..."
until ping -c1 -W1 "$host" >/dev/null 2>&1; do
  sleep 2
done

exec uvicorn processing_node:app --host 0.0.0.0 --port 5000
