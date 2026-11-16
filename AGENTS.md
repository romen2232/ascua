# ascua — agent guidance

ascua is a self-hosted, privacy-first personal finance and FIRE app for people living in Spain.

Read first: `docs/superpowers/specs/2026-11-16-ascua-v1-design.md` (v1 design),
`docs/roadmap.md` (what v1 leaves out), `docs/superpowers/plans/` (implementation plans, one per slice).

## Rules
- Backend is DDD + Screaming Architecture: `backend/<context>/{domain,application,infrastructure,api}`.
  `domain` and `application` never import django, rest_framework or celery (import-linter enforces it).
- Every tenant table uses `TenantManager` and a forced RLS migration; the app runs as `ascua_app`.
- Every API route is registered in `backend/tests/isolation/registry.py`; denied access is 404.
- Money is integer cents, shares/percentages integer basis points, dates ISO 8601. No floats.
- No hard-coded tax values: rule packs in `rules/` with a source link and golden tests.
- All user-facing strings in Spanish and English. No telemetry, trackers, external fonts or CDNs.
- Tests first. Conventional Commits, no AI attribution.

## Commands
- Dev database: `docker compose -f compose.dev.yaml up -d` (PostgreSQL 17 on port 5442)
- Migrate: `cd backend && ASCUA_DB_USER=ascua_owner uv run python manage.py migrate`
- All checks: `scripts/check.sh`
