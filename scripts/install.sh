#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> Installing EcoSphere dependencies"

if ! command -v node >/dev/null 2>&1; then
  echo "Node.js is required. Install Node.js 20+ and retry."
  exit 1
fi

if ! command -v python3.12 >/dev/null 2>&1; then
  echo "Python 3.12 is required. Install Python 3.12+ and retry."
  exit 1
fi

cd "$ROOT_DIR"

echo "==> Installing root tooling"
npm install

echo "==> Installing frontend dependencies"
npm --prefix frontend install

echo "==> Setting up backend virtual environment"
cd "$ROOT_DIR/backend"
if [ ! -d ".venv" ]; then
  python3.12 -m venv .venv
fi
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "Created backend/.env from .env.example"
fi

cd "$ROOT_DIR/frontend"
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "Created frontend/.env from .env.example"
fi

cd "$ROOT_DIR"
npx husky init 2>/dev/null || true
if [ -d ".husky" ]; then
  echo "npx lint-staged" > .husky/pre-commit
  chmod +x .husky/pre-commit
fi

echo "==> Installation complete"
echo "Next steps:"
echo "  1. Start PostgreSQL (or run: docker compose up -d postgres)"
echo "  2. Run migrations: cd backend && source .venv/bin/activate && alembic upgrade head"
echo "  3. Start development: npm run dev"
