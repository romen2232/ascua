#!/usr/bin/env bash
# Runs every check CI runs. Exits non-zero on the first failure.
set -euo pipefail
cd "$(dirname "$0")/../backend"
uv run ruff check .
uv run ruff format --check .
uv run mypy .
uv run lint-imports
uv run python manage.py compilemessages --ignore ".venv/*" > /dev/null
uv run pytest -q
if [ -f ../app/package.json ]; then
  cd ../app
  npm run lint
  npm run typecheck
  npm test -- --ci
fi
