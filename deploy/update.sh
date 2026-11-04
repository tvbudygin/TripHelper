#!/usr/bin/env bash
# Загружает собранный образ и обновляет приложение, сохраняя данные
set -euo pipefail
cd /opt/triphelper
exec 9>.deploy.lock
flock -n 9 || { echo "Выкладка уже идёт"; exit 1; }
release="${1:?Specify commit SHA}"
[[ "$release" =~ ^[a-f0-9]{40}$ ]] || exit 1
test -f .env
test -f incoming/image.tar.gz
docker load -i incoming/image.tar.gz
mkdir -p nginx backups
chmod 700 backups
# Перед обновлением сохраняем существующую базу
if docker compose -f compose.yml ps --status running --services 2>/dev/null | grep -qx db; then
  docker compose -f compose.yml exec -T db pg_dump -U triphelper -d triphelper -Fc > "backups/before-$release.dump"
fi
cp incoming/compose.yml compose.yml
cp incoming/nginx/http.conf nginx/http.conf
cp incoming/nginx/https.conf.template nginx/https.conf.template
cp incoming/enable-https.sh incoming/renew-cert.sh ./
if [ ! -f nginx/active.conf ]; then cp nginx/http.conf nginx/active.conf; fi
# Меняем только образ, остальные настройки остаются в серверном .env
sed -i '/^APP_IMAGE=/d' .env
printf '\nAPP_IMAGE=triphelper:%s\n' "$release" >> .env
docker compose -f compose.yml up -d --wait --wait-timeout 180 db app
# После замены приложения nginx должен заново разрешить его адрес
docker compose -f compose.yml up -d --force-recreate nginx
docker compose -f compose.yml exec -T nginx nginx -t
# Проверяем ответ приложения после перехода на HTTPS
docker compose -f compose.yml exec -T nginx wget -qO- http://app:8000/api/health | grep -q '"status":"ok"'
rm incoming/image.tar.gz
echo "Обновлено: $release"
