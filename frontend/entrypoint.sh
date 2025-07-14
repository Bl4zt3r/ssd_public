#!/bin/sh

envsubst '${UPSTREAM_HOST} ${UPSTREAM_PORT}' < /etc/nginx/nginx.conf.template > /etc/nginx/conf.d/default.conf
exec nginx -g 'daemon off;'
