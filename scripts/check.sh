#!/usr/bin/env bash
# Runs every check CI runs. Exits non-zero on the first failure.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

cd "$ROOT/backend"
uv run ruff check .
uv run ruff format --check .
uv run mypy .
uv run lint-imports
uv run python manage.py compilemessages --ignore ".venv/*" > /dev/null
uv run pytest -q
uv run python manage.py spectacular --file openapi.json --format openapi-json

if [ -f "$ROOT/app/package.json" ]; then
  if ! command -v npm > /dev/null && [ -s "${NVM_DIR:-$HOME/.nvm}/nvm.sh" ]; then
    # shellcheck disable=SC1091
    . "${NVM_DIR:-$HOME/.nvm}/nvm.sh" > /dev/null
  fi
  cd "$ROOT/app"
  # The committed API types must match the backend's current schema.
  npm run -s api:generate > /dev/null
  git diff --exit-code -- src/api/schema.d.ts
  npm run -s lint
  npm run -s typecheck
  CI=1 npm test -s -- --ci
fi
