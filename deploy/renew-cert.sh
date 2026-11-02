#!/usr/bin/env bash
# Продлевает сертификат и перечитывает его в nginx
set -euo pipefail
cd /opt/triphelper
docker compose -f compose.yml run --rm certbot renew --quiet
docker compose -f compose.yml exec -T nginx nginx -s reload
