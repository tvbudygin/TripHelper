#!/bin/bash

# bash start.sh
set -e

docker compose up -d --build --wait

echo ""
echo "TripHelper успешно запущен!"
echo "Перейдите на http://localhost:8000"