#!/usr/bin/env bash
set -euo pipefail

attempts="${APT_UPDATE_ATTEMPTS:-5}"

for attempt in $(seq 1 "${attempts}"); do
  rm -rf /var/lib/apt/lists/*
  mkdir -p /var/lib/apt/lists/partial

  if apt-get update \
    -o Acquire::Retries=5 \
    -o Acquire::http::No-Cache=true \
    -o Acquire::https::No-Cache=true; then
    exit 0
  fi

  if [ "${attempt}" = "${attempts}" ]; then
    exit 1
  fi

  sleep $((attempt * 5))
done
