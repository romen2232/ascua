# ascua — guidance for Claude Code and OpenCode

ascua is a self-hosted, privacy-first app that estimates how far each user is from financial
independence in Spain and how to withdraw with the least tax. Read these first:

- `requirements.md` — product requirements; every requirement has an ID (USR-1, NW-2, TAX-3, …).
- `.specify/memory/constitution.md` — non-negotiable principles. It overrides this file.
- `specs/NNN-feature/` — spec, plan and tasks for each feature.

## Status

Specification phase. No application code exists yet; do not write any until a feature has an
approved `spec.md`, `plan.md` and `tasks.md`.

## Workflow (GitHub Spec Kit)

Spec Kit is installed for both agents (`claude` + `opencode`, see `.specify/integration.json`).
Use the invocation style of your agent:

- Claude Code: `/speckit-specify`, `/speckit-clarify`, … (hyphen)
- OpenCode: `/speckit.specify`, `/speckit.clarify`, … (dot)

1. Specify with the feature's requirement IDs → `spec.md` (behaviour only, no
   implementation).
2. Clarify → resolve open questions in the spec.
3. Plan → `plan.md` (models, serializers, endpoints, Celery tasks, screens). Must pass the
   Constitution Check.
4. Tasks → `tasks.md`; analyze to check spec/plan/tasks consistency.
5. Implement. In every task, write the tests first and see them fail.
6. Behaviour change → update the spec first, then regenerate plan and tasks. Never fix drift only in
   code.

Git extension (`git`) is installed for both agents: feature branch creation, validation,
remote detection, and auto-commit hooks before/after Spec Kit commands.

Every requirement ID must trace to a spec, a task and a test.

## Phase 1 specs

| Spec | Requirements |
| --- | --- |
| 001-users-households | USR-1 to USR-6, NF-2, NF-3, NF-6 |
| 002-accounts-import | NW-1 to NW-3; one importer task per bank or broker |
| 003-spending | SP-1 to SP-3 |
| 004-fire-engine | FI-1 to FI-3, AL-1 |
| 005-ops | NF-1, NF-7, NF-8, NF-10, NF-11 |

## Repository layout (planned)

```
AGENTS.md
CLAUDE.md
requirements.md
.specify/memory/constitution.md
specs/NNN-feature/{spec,plan,tasks}.md
backend/            # Django + DRF
backend/taxengine/  # pure Python, no Django imports
rules/ES/<year>/    # YAML rule packs
mobile/             # React Native (Expo)
```

## Commands

Planned in `specs/001-users-households/plan.md`; they work once the scaffold exists.

- Dev services: `docker compose -f compose.dev.yaml up -d` (PostgreSQL 17 + Redis 8)
- Backend (from `backend/`): `uv run pytest` · `uv run ruff check . && uv run ruff format --check .`
  · `uv run mypy .`
- Isolation suite only: `uv run pytest tests/isolation`
- Tax engine only (must run without Django): `uv run pytest taxengine`
- Mobile (from `mobile/`): `npm test` · `npm run lint` · `npm run typecheck`
- Regenerate TypeScript API client: `npm run api:generate` (from the backend's OpenAPI schema)
- Full stack: `docker compose up` (NF-1, spec 005)

## Stack (from spec 001 plan)

Python 3.13, Django 5.2 LTS, DRF, drf-spectacular, SimpleJWT, django-otp, argon2-cffi, django-axes,
Authlib, Celery + Redis 8, PostgreSQL 17 with row-level security. Mobile: Expo, TypeScript strict,
expo-router, TanStack Query, openapi-fetch, i18next.

## Rules

- Never hardcode a tax rate, limit, threshold or legal age; read it from a rule pack in `rules/`.
  Every rule-pack value needs a BOE, AEAT or Seguridad Social source link and golden tests.
- `backend/taxengine/` must not import Django and must stay deterministic.
- Every queryset is scoped by user or household; add a cross-user isolation test for every new
  endpoint. Follow `specs/001-users-households/contracts/isolation.md`: tenant models use
  `TenantManager` and an RLS migration, views use `ScopedViewSet`, every route is registered in
  `backend/tests/isolation/registry.py`, and every tenant model is covered by export and deletion.
- Shareable entities (accounts, assets, …) link to `sharing.Item` with a one-to-one field; never
  add owner or sharing columns of their own.
- Money is integer cents (or `Decimal`), never float. Dates are ISO 8601.
- All user-facing strings go through translation files (Spanish and English).
- Regenerate the TypeScript API client after any serializer change.
- No telemetry, trackers, external fonts or CDNs. Connectors are opt-in and off by default.
- Show consequences of user-defined scenarios; never recommend buying or selling a product.
