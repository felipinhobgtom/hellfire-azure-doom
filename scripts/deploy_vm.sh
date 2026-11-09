#!/usr/bin/env bash
set -euo pipefail

cd /opt/hellfire
git fetch --prune origin main
git reset --hard origin/main
git submodule update --init --recursive

docker build --tag hellfire:latest /opt/hellfire
docker rm -f hellfire || true
docker run --detach --restart unless-stopped --name hellfire \
  --network hellfire \
  --volume /opt/hellfire/data:/data \
  hellfire:latest
docker restart caddy
