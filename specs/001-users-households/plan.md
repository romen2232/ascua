# Implementation Plan: Users, Households and Data Isolation

**Branch**: `001-users-households` | **Date**: 2026-10-29 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-users-households/spec.md`

## Summary

Build the identity and tenancy foundation every later ascua feature depends on: invitation-only
sign-up, mandatory TOTP two-factor (or an external OIDC provider), server-tracked sessions with 30/90-day
limits, personal access tokens, individual tax profiles, households with owner/member/viewer roles,
a generic ownership-and-sharing model for "items" that later specs attach to, time-limited
read-only support access with an append-only log, and GDPR export and deletion.

Isolation is enforced twice: tenant-scoped Django managers that refuse unscoped queries, and
PostgreSQL row-level security driven by per-transaction actor context. A registry-driven test suite
fails the build if any route or tenant table lacks isolation coverage. See [research.md](research.md).

## Technical Context

**Language/Version**: Python 3.13 (backend, tax engine); TypeScript 5 strict (mobile)

**Primary Dependencies**: Django 5.2 LTS, Django REST Framework 3.16, drf-spectacular,
djangorestframework-simplejwt, django-otp, argon2-cffi, django-axes, Authlib (OIDC), Celery 5.5,
PyYAML + jsonschema (tax engine); Expo (current stable SDK), expo-router, TanStack Query,
openapi-typescript + openapi-fetch, i18next, expo-secure-store, expo-local-authentication

**Storage**: PostgreSQL 17 with row-level security (roles `ascua_owner` and `ascua_app`); Redis 8
(Celery broker, session-revocation cache, throttling); private file storage volume for exports

**Testing**: pytest, pytest-django, factory-boy, Hypothesis, time-machine; ruff, mypy
(django-stubs); Jest + React Native Testing Library, ESLint, `tsc --noEmit`

**Target Platform**: Linux server on arm64 (Raspberry Pi 4) and amd64 via Docker; iOS 16+ and
Android 10+ through Expo

**Project Type**: mobile app + REST API (monorepo: `backend/`, `mobile/`, `rules/`)

**Performance Goals**: sign-in (password + two-factor) under 1 s server time on a Pi 4; scoped API
reads p95 under 200 ms on a Pi 4; export of 50,000 records ready within 5 minutes (SC-004)

**Constraints**: no outbound network calls except the configured OIDC provider and SMTP; works with
both disabled; Argon2id memory cost of 64 MiB per hash; all strings in `es` and `en`

**Scale/Scope**: one instance serves about 2–20 users and a few households; around 50 endpoints and
about 15 mobile screens in this feature

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | How this plan complies | Pre | Post |
| --- | --- | --- | --- |
| I. Privacy-first self-hosting | No telemetry or third-party push (R7); OIDC and SMTP are admin-configured and optional; admins see metadata only (FR-016); support access is read-only, time-limited and logged (R3) | ✅ | ✅ |
| II. Data-layer isolation | Tenant managers plus RLS with `FORCE`, fail-closed context (R2); 404 for denied; registry-driven isolation suite that breaks the build on gaps ([isolation.md](contracts/isolation.md)) | ✅ | ✅ |
| III. Rules as data | Region list from `rules/ES/regions.yaml` with schema and source links (R10); disability thresholds and family minimums are deferred to rule packs, not encoded here | ✅ | ✅ |
| IV. Simulation, not advice | Disclaimer acknowledged at first sign-in (FR-013); no product content in this feature | ✅ | ✅ |
| V. Exact money and transparent maths | Shares in integer basis points with a DB-enforced total (R9); goal amounts in integer cents; ISO dates | ✅ | ✅ |
| VI. Pure, golden-tested tax engine | `backend/taxengine/` created with no Django import, enforced by a test run in an environment without Django; this feature only loads regions, so golden tax cases start in spec 002+ | ✅ | ✅ |
| VII. Test-first, spec-first | Requirement IDs trace from spec to tasks; tasks will put tests before implementation | ✅ | ✅ |
| Tech constraints | Stack matches the constitution. `dj-rest-auth` (suggested in requirements, not the constitution) is replaced by plain SimpleJWT views (R4) | ✅ | ✅ |

**Result**: PASS. No violations, so Complexity Tracking is empty.

## Project Structure

### Documentation (this feature)

```text
specs/001-users-households/
├── spec.md
├── plan.md                 # This file
├── research.md             # Phase 0
├── data-model.md           # Phase 1
├── quickstart.md           # Phase 1
├── contracts/
│   ├── api.md              # REST endpoint inventory
│   ├── export-format.md    # Export v1 format
│   └── isolation.md        # Isolation rules + test registry contract
├── checklists/requirements.md
└── tasks.md                # Phase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
compose.dev.yaml                 # PostgreSQL + Redis for development (production compose: spec 005)
rules/
├── schema/regions.schema.json
└── ES/regions.yaml
backend/
├── pyproject.toml               # uv; ruff, mypy, pytest config
├── manage.py
├── ascua/                       # settings/, urls.py, celery.py, asgi/wsgi
├── core/
│   ├── rls/                     # actor context, SQL helpers, enable_rls migration op, system allow-list
│   ├── tenancy.py               # Actor, TenantManager, UnscopedQueryError
│   ├── api.py                   # ScopedViewSet, error format, ETag/If-Match
│   └── registries.py            # export sections, deletion handlers/blockers
├── apps/
│   ├── accounts/                # User, invitations, sign-up/sign-in, MFA, OIDC, sessions, PATs, admin, InstanceSettings, CLI
│   ├── profiles/                # TaxProfile, RegionResidence, Dependant, SocialSecuritySummary
│   ├── households/              # Household, membership, goals, household invitations
│   ├── sharing/                 # Item, OwnershipShare, OwnershipChangeRequest, SharingSetting, ViewerGrant
│   ├── support/                 # SupportGrant, AccessLogEntry, /support mirrors
│   ├── privacy/                 # ExportJob, export builder + schemas/, deletion
│   └── notifications/
├── taxengine/                   # pure Python: rules/ loader, regions; own tests/
├── locale/{es,en}/LC_MESSAGES/
└── tests/
    ├── fixtures/sampleitem/     # test-only item kind (R8)
    ├── unit/
    ├── integration/
    ├── contract/
    └── isolation/               # registry.py, test_api_isolation.py, test_rls_sql.py, test_coverage.py
mobile/
├── package.json
├── app/                         # expo-router routes: (auth)/, (app)/profile, household, sharing, settings, privacy
├── src/
│   ├── api/                     # generated client (do not edit) + fetch wrapper with token refresh
│   ├── auth/                    # secure token storage, app lock
│   ├── features/                # profile, household, sharing, support, privacy
│   ├── i18n/{es,en}.json
│   └── ui/                      # shared accessible components
└── __tests__/
```

**Structure Decision**: a monorepo with a Django backend split into focused apps, a pure
`taxengine` package inside `backend/` (as the requirements lay out) and an Expo app in `mobile/`.
Rule packs live at the root in `rules/`, so contributors can change them without touching code.

## Implementation Phases (input for `/speckit-tasks`)

1. **Foundation**: repo scaffolding, dev compose, settings, DB roles, `core/rls` + `TenantManager`,
   the isolation suite skeleton (it must fail on an unregistered route before any route exists),
   error format, i18n setup, `taxengine` + region pack, mobile scaffold and generated client
   pipeline.
2. **US1 + US3 (P1)**: invitations, `ascua_init`, sign-up with mandatory TOTP, two-step sign-in,
   throttling, sessions, PATs, admin user metadata; isolation cases for each route.
3. **US2 (P1)**: tax profile, region history, dependants, Social Security summary, disclaimer;
   mobile onboarding screens.
4. **US4 (P2)**: households, roles, goals; items, ownership shares with pending offers and change
   requests, sharing settings, totals helper; mobile household and sharing screens.
5. **US6 (P2)**: support grants, read-only support mirrors, append-only log, expiry beat task.
6. **US7 (P2)**: export registry, builder and schema v1; deletion blockers, relinquish flow and
   `ascua.delete_user`.
7. **US5 (P3)**: viewer grants.
8. **OIDC (FR-006)**: provider flow and linking, after US1 is stable.
9. **Polish**: app lock, accessibility labels, translations review, quickstart run-through.

## Post-Design Constitution Re-check

Re-evaluated after writing data-model and contracts: still PASS. Design points that strengthen
compliance: append-only log enforced by DB grants (Principle II/I), support mode as a read-only
transaction (I), integer basis points with a commit-time invariant (V), and a coverage test tying
every tenant model to RLS, export and deletion (II, NF-6).

## Complexity Tracking

No violations to justify.
