#!/bin/sh
set -eu

sed -i "s/DOMAIN/${DOMAIN}/g" /etc/nginx/conf.d/default.conf
sed -i "s/ADMIN_BASE_URL/${ADMIN_BASE_URL}/g" /etc/nginx/conf.d/default.conf

exec nginx -g 'daemon off;'
