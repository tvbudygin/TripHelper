#!/usr/bin/env bash
# Получает сертификат для домена и включает HTTPS
set -euo pipefail
cd /opt/triphelper
domain="${1:?Specify domain}"
email="${2:?Specify email}"
[[ "$domain" =~ ^[a-zA-Z0-9.-]+$ ]] || exit 1
docker compose -f compose.yml run --rm certbot certonly --webroot -w /var/www/certbot --cert-name triphelper -d "$domain" --email "$email" --agree-tos --non-interactive
sed "s/DOMAIN/$domain/g" nginx/https.conf.template > nginx/active.conf
docker compose -f compose.yml exec -T nginx nginx -t
docker compose -f compose.yml exec -T nginx nginx -s reload
