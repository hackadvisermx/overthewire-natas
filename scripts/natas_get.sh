#!/usr/bin/env bash
# Uso: natas_get.sh <nivel_num> <password> [path] [curl_extra_args...]
# Hace un GET autenticado (HTTP Basic Auth) a natasN.natas.labs.overthewire.org
set -euo pipefail

LEVEL="$1"
PASS="$2"
PATHPART="${3:-/}"
shift 3 || shift $#
USER="natas${LEVEL}"
HOST="natas${LEVEL}.natas.labs.overthewire.org"

curl -s -u "${USER}:${PASS}" "http://${HOST}${PATHPART}" "$@"
