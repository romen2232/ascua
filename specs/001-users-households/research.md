# Research: Users, Households and Data Isolation

**Feature**: 001-users-households | **Date**: 2026-10-29 | **Plan**: [plan.md](plan.md)

Each entry records a decision, why it was chosen, and what else was considered. Library versions are
the minimum lines to pin at scaffold time; exact versions are locked in `uv.lock` and
`package-lock.json`.

## R1. Runtime and framework versions

- **Decision**: Python 3.13, Django 5.2 LTS, Django REST Framework 3.16, drf-spectacular,
  PostgreSQL 17, Redis 8, Celery 5.5. Dependency management with `uv`.
- **Rationale**: Django 5.2 is the current LTS (supported to April 2028), so the self-hosted
  install base does not need a framework upgrade every eight months. PostgreSQL 17 and Redis 8 ship
  official arm64 images that run on a Raspberry Pi 4. Redis 8's open-source edition (AGPLv3) runs
  as a separate container, so it does not affect ascua's MIT licence.
- **Alternatives**: Django 6.0 (shorter support window); Valkey instead of Redis (BSD-licensed,
  protocol-compatible). Valkey stays a documented drop-in replacement, but the default follows the
  constitution's "Celery + Redis".

## R2. Isolation: two layers

- **Decision**:
  1. **App layer**: every tenant-owned model's default manager refuses to build a query without an
     actor (`Model.objects.for_actor(actor)`); calling `.all()`/`.filter()` unscoped raises
     `UnscopedQueryError`. A separate `Model.unscoped` manager exists only for migrations and
     audited system tasks. DRF viewsets inherit from a `ScopedViewSet` that takes the actor from the
     request.
  2. **Database layer**: PostgreSQL row-level security (RLS) with `FORCE ROW LEVEL SECURITY` on every
     tenant table. The web and worker processes connect as `ascua_app` (no `BYPASSRLS`, not table
     owner). Migrations run as `ascua_owner`. Each request or task runs inside a transaction that sets
     `SET LOCAL app.actor_id`, `app.actor_mode` (`self` | `support` | `system`) and, for support,
     `app.subject_id`. Policies call `STABLE SECURITY DEFINER` helper functions
     (`ascua.can_read_item(id)`, `ascua.can_write_item(id)`, `ascua.actor_household_id()`) that are
     owned by `ascua_owner` with a fixed `search_path`, which avoids recursive policy evaluation.
- **Rationale**: the constitution makes this non-negotiable. `SET LOCAL` is scoped to a transaction,
  so a pooled connection cannot leak one user's context into another request. Requests therefore run
  in `ATOMIC_REQUESTS` mode, and Celery tasks use an `actor_context()` context manager that opens
  the transaction.
- **Alternatives**: one schema per user (heavy migrations, poor household joins); app-layer only
  (the constitution forbids it); `django-rls` style packages (thin, unmaintained; the SQL is small
  enough to own).

## R3. Support access as a read-only database transaction

- **Decision**: admins reach a user's data only through `/api/v1/support/{user_id}/…` endpoints.
  These require an active `SupportGrant`, set `app.actor_mode = 'support'` and
  `app.subject_id = <user>`, and run `SET TRANSACTION READ ONLY`. RLS read policies accept support
  mode for rows owned by the subject only, never items merely shared with or granted to them. Each
  response writes an `AccessLogEntry` in a separate autocommit write made through
  `ascua.log_support_access(...)`, a `SECURITY DEFINER` function that is the only path allowed to
  insert during support mode.
- **Rationale**: read-only is enforced by PostgreSQL itself, not by remembering to omit write
  routes. The spec's edge case ("never items merely granted to them") maps to one policy clause.
- **Alternatives**: impersonation with a full user session (writes possible, audit harder).

## R4. Authentication stack

- **Decision**:
  - Passwords: Django's `Argon2PasswordHasher` (Argon2id) via `argon2-cffi`, tuned to
    `memory_cost=65536` KiB, `time_cost=3`, `parallelism=2`. Validators: minimum length 12 and
    Django's common-password list.
  - Two-factor: `django-otp` with `TOTPDevice` (SHA-1, 30 s, 6 digits for authenticator-app
    compatibility) and `StaticDevice` for 10 single-use recovery codes.
  - Tokens: `djangorestframework-simplejwt` with 10-minute access tokens and rotating refresh tokens.
    Each refresh token carries a `sid` claim linking to a server-side `DeviceSession` row, which
    enforces the 30-day idle and 90-day absolute limits (FR-008a), lets users list and end sessions
    (FR-008), and is checked on every request through a Redis-cached lookup so ending a session takes
    effect at once.
  - Two-step sign-in: `POST /auth/login` returns a 5-minute single-use `mfa_token`, not session
    tokens. `POST /auth/login/mfa` exchanges it plus a TOTP or recovery code for tokens.
  - Throttling: `django-axes` locks out after 5 failures per username + IP for 15 minutes, plus DRF
    `ScopedRateThrottle` on the auth endpoints (FR-007).
  - Personal access tokens: own model storing a SHA-256 hash of a random 32-byte secret, shown once
    with prefix `ascua_pat_`, scopes `read` or `read_write`, required expiry of at most 1 year. A
    custom DRF authentication class resolves them to the owner's actor.
- **Rationale**: the hasher parameters keep login under ~400 ms on a Pi 4 while staying memory-hard.
  The two-step flow means a stolen password alone never yields a token.
- **Alternatives**: `dj-rest-auth`, which the requirements suggest. It is not used: its login view
  issues tokens after the password step, and its registration path depends on django-allauth's
  browser flows, so both the mandatory two-factor step and invitation-only sign-up would need
  overriding. Plain SimpleJWT views are simpler. This is a deviation from the requirements'
  suggested stack, not from the constitution. Opaque DB-backed tokens only were also rejected:
  workable, but JWT access tokens avoid a DB hit per request for the common case.

## R5. External identity provider (OIDC)

- **Decision**: the backend is the OIDC client (authorization code + PKCE, confidential client,
  library: Authlib). The app opens `GET /auth/oidc/start?invitation=<token>` in the system browser.
  The backend redirects to the provider; on callback it validates the ID token, then redirects to the
  app deep link `ascua://auth/callback?code=<one-time code>`. The app exchanges the code at
  `POST /auth/oidc/exchange` for ascua tokens. The account is matched by the stored
  `(issuer, subject)` pair. On first sign-in it is linked through the invitation token carried in
  `state`, and the invitation's email must equal the provider's verified email.
- **Rationale**: one place configures the provider (environment variables on the server), and the
  client secret never ships in the app. Works with Authelia, Authentik and Keycloak, which all
  support standard discovery.
- **Alternatives**: the app as a public client sending an ID token to the backend (the backend would
  still have to validate audience and nonce, and every app build would need the provider config);
  `mozilla-django-oidc` (session-cookie oriented, a poor fit for a mobile client).

## R6. Mobile app

- **Decision**: Expo (current stable SDK at scaffold time) with TypeScript strict mode, expo-router,
  TanStack Query, `openapi-typescript` + `openapi-fetch` for the generated client, i18next with JSON
  locale files (`es`, `en`), `expo-secure-store` for the refresh token, `expo-local-authentication`
  for the app lock.
  - App lock (FR-008a): an `AppState` listener records when the app goes to the background. On
    return after more than 300 s, a lock screen covers the navigator until `authenticateAsync()`
    succeeds. If `getEnrolledLevelAsync()` reports no device security, the app shows a blocking
    screen asking the user to set a device lock.
  - Testing: Jest + React Native Testing Library; ESLint, Prettier, `tsc --noEmit`.
- **Rationale**: matches the requirements; the generated client keeps the app honest about the API
  contract.
- **Alternatives**: React Navigation without expo-router (more boilerplate); Orval (heavier code
  generation).

## R7. Notifications without leaving the instance

- **Decision**: in-app notifications stored in a `Notification` table and polled by the app (on
  focus and every 60 s while open), plus optional email when SMTP is configured. No mobile push in
  this feature.
- **Rationale**: Expo and APNs/FCM push send data through third parties, which violates Principle I
  unless opt-in. An opt-in push connector can be specified later.
- **Alternatives**: Expo push by default (rejected for privacy).

## R8. Generic "item" for ownership and sharing

- **Decision**: a concrete `sharing.Item` table (`id`, `kind`, `created_by`, `version`) that owns
  `OwnershipShare` and `SharingSetting` rows. Later features attach their entities with
  `item = OneToOneField(Item)` (e.g. `Account` in spec 002), and RLS policies on those tables
  delegate to `ascua.can_read_item(item_id)`. Feature 001 ships the item machinery with its tests
  run against a test-only model (`tests/fixtures/sampleitem`); the user-visible acceptance with real
  accounts completes in spec 002.
- **Rationale**: a real foreign key keeps referential integrity and lets one RLS helper protect every
  future shareable entity. Generic foreign keys (`contenttypes`) cannot be used inside RLS policies
  or foreign key constraints.
- **Alternatives**: duplicating owner and sharing columns on each entity (inconsistent rules);
  `GenericForeignKey` (no integrity, hard to secure).

## R9. Ownership percentages

- **Decision**: store shares as integer basis points (0–10,000 = 0.00–100.00%). A deferred
  constraint trigger checks that the accepted + pending + external shares for each item sum to
  exactly 10,000 at commit. Splitting a share uses largest-remainder rounding so totals stay exact
  (e.g. 100% split three ways = 3334/3333/3333).
- **Rationale**: exact arithmetic (Principle V) and a database-enforced invariant.
- **Alternatives**: `Decimal(5,2)` (works, but integer arithmetic is simpler to keep exact across
  Python, SQL and TypeScript).

## R10. Region list from rule packs

- **Decision**: `rules/ES/regions.yaml` lists the 19 territories (17 autonomous communities plus
  Ceuta and Melilla) with INE code, names in Spanish and English, a `regime: common | foral` flag and
  a source link. It is validated by a JSON Schema in `rules/schema/`. `taxengine.rules.load_regions()`
  (pure Python, PyYAML + `jsonschema`) reads it; Django exposes it via `GET /api/v1/reference/regions`.
- **Rationale**: Principle III, even for reference data. This also gives the tax engine its first
  real module and loader to grow from.
- **Alternatives**: a Django `choices` enum (hardcoded).

## R11. Export and deletion extensibility

- **Decision**:
  - Export: a registry where each app registers an `ExportSection` (name, JSON serializer, CSV
    columns). A Celery task builds `ascua-export-<user>-<timestamp>.zip` containing `export.json`
    (with `format: "ascua-export"`, `format_version: 1`) and one CSV per section. It is written to the
    private media volume, downloadable only through an authenticated endpoint, and removed after
    7 days by a beat task.
  - Deletion: a registry of `DeletionBlocker`s (household ownership, co-owned items, last admin) and
    `DeletionHandler`s. The final delete runs `ascua.delete_user(uid)`, a `SECURITY DEFINER`
    function that removes rows across RLS-protected and append-only tables in one transaction.
- **Rationale**: FR-032 obliges later features to extend export and deletion; a registry makes that
  a one-line obligation. A test fails if a tenant model is not covered by any section or handler.
- **Alternatives**: Django's `dumpdata` (exposes internal fields, no CSV, not user-scoped).

## R12. Append-only access log

- **Decision**: the `ascua_app` role has `INSERT` and `SELECT` only on `support_accesslogentry`; a
  trigger also rejects `UPDATE`. Deletion happens only through `ascua.delete_user`.
- **Rationale**: "cannot be edited or deleted by anyone" (User Story 6) is enforced below the app.

## R13. Optimistic concurrency

- **Decision**: editable shared resources carry an integer `version`. Responses include
  `ETag: "<version>"`; `PATCH`/`PUT` require `If-Match` and return `412 Precondition Failed` on
  mismatch.
- **Rationale**: implements the concurrent-edit edge case with standard HTTP semantics.

## R14. First-run setup

- **Decision**: `python manage.py ascua_init` (run with `docker compose exec`) creates
  `InstanceSettings` and an admin invitation, and prints a one-time sign-up link. It refuses to run
  if any user already exists. The admin then signs up like anyone else, with two-factor.
- **Rationale**: no unauthenticated "claim this server" web endpoint for an attacker to race on a
  freshly exposed instance.

## R15. Testing strategy

- **Decision**:
  - Backend: pytest, pytest-django, factory-boy, Hypothesis (share arithmetic), freezegun or
    time-machine (expiries).
  - Static checks: ruff (lint + format), mypy with django-stubs and djangorestframework-stubs.
  - Contract tests: compare the generated OpenAPI schema with `contracts/api.md` endpoint
    inventory.
  - Isolation suite: (a) API-level, a parametrised test over every route in the OpenAPI schema;
    each route must be registered in `tests/isolation/registry.py` with fixtures, and an
    unregistered route fails the build (SC-002). (b) Database-level, raw SQL as `ascua_app` under
    another actor's context returns zero rows for every tenant table.
- **Rationale**: makes Principle II mechanically enforced as the codebase grows.
