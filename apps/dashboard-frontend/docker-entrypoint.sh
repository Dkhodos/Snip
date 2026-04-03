#!/bin/sh
set -e

# Substitute BACKEND_URL into nginx config (restrict to that var so nginx
# variables like $uri, $proxy_host etc. are preserved)
envsubst '${BACKEND_URL}' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf

exec nginx -g 'daemon off;'
