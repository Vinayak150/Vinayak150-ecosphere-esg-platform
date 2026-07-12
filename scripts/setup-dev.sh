#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> Starting EcoSphere development environment"

cd "$ROOT_DIR"

if ! docker compose ps postgres 2>/dev/null | grep -q "running"; then
  echo "==> Starting PostgreSQL container"
  docker compose up -d postgres
fi

echo "==> Waiting for PostgreSQL"
until docker compose exec -T postgres pg_isready -U ecosphere -d ecosphere >/dev/null 2>&1; do
  sleep 1
done

cd "$ROOT_DIR/backend"
if [ ! -d ".venv" ]; then
  echo "Virtual environment not found. Run ./scripts/install.sh first."
  exit 1
fi

source .venv/bin/activate
alembic upgrade head

cd "$ROOT_DIR"
npm run dev
