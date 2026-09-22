#!/bin/bash
# Healthcheck контейнера OSRM.
#
# В образе ghcr.io/project-osrm/osrm-backend нет ни wget, ни curl, поэтому
# HTTP-запрос к самому OSRM делаем средствами bash через /dev/tcp:
# запрашиваем реальный маршрут (Минск → Борисов) и проверяем код ответа.
set -euo pipefail

PORT=5000
REQUEST="GET /route/v1/driving/27.5615,53.9006;28.5,54.2279?overview=false HTTP/1.0"

exec 3<>"/dev/tcp/127.0.0.1/${PORT}"
printf '%s\r\nHost: localhost\r\nConnection: close\r\n\r\n' "$REQUEST" >&3

# timeout на чтение: OSRM может держать соединение открытым
IFS= read -r -t 5 -u 3 status_line

grep -q '200 OK' <<<"$status_line"
