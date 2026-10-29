# Quickstart: Validate Users, Households and Data Isolation

**Feature**: 001-users-households | **Plan**: [plan.md](plan.md)

How to prove the feature works end to end once implemented. Endpoint details are in
[contracts/api.md](contracts/api.md); isolation rules are in
[contracts/isolation.md](contracts/isolation.md).

## Prerequisites

- Docker with Compose v2; `uv` (Python 3.13); Node.js 22 LTS; an authenticator app (or `oathtool`
  for scripted TOTP codes).
- For the mobile checks: Expo Go or a development build on a device with a screen lock enabled.

## Setup

```bash
docker compose -f compose.dev.yaml up -d          # PostgreSQL 17 + Redis 8
cd backend
uv sync
uv run python manage.py migrate                   # runs as ascua_owner, creates ascua_app role grants
uv run python manage.py ascua_init                # prints the one-time admin sign-up link
uv run python manage.py runserver 0.0.0.0:8000 &
uv run celery -A ascua worker -B -l info &
cd ../mobile && npm install && npm run api:generate && npx expo start
```

## Automated validation

| Check | Command | Expect |
| --- | --- | --- |
| Unit + integration | `cd backend && uv run pytest` | All pass |
| Isolation suite | `uv run pytest tests/isolation -q` | All pass; zero routes or tenant models unregistered (SC-002) |
| RLS at database level | `uv run pytest tests/isolation/test_rls_sql.py` | Zero rows visible across actors; fail closed without context |
| Contract | `uv run pytest tests/contract` | OpenAPI routes match `contracts/api.md`; export validates against schema v1 |
| Tax engine (pure) | `uv run pytest taxengine` | Runs without Django installed in the environment |
| Lint/types | `uv run ruff check . && uv run mypy .` | Clean |
| Mobile | `cd mobile && npm run lint && npm run typecheck && npm test` | Clean, all pass |

## Manual scenarios (map to spec user stories)

1. **Sign-up with mandatory two-factor (US1)**: open the `ascua_init` link in the app; set a
   12+ character password, scan the QR code and confirm a code. Expect recovery codes to be shown,
   then the disclaimer and the profile screen. Reopening the link → "invitation invalid".
   Signing up without an invitation → refused.
2. **Sign-in (US1)**: sign out, sign in. A wrong code fails; 5 wrong passwords → throttled with a
   retry time.
3. **App lock (FR-008a)**: background the app for more than 5 minutes and reopen → device
   biometric/PIN prompt before any data. On an emulator with no lock → blocking "set a device lock"
   screen.
4. **Profile (US2)**: the region list shows 19 entries, with Navarra and País Vasco marked foral. A
   future birth date is rejected. Change region with an effective date; history shows both.
5. **Household and sharing (US4)**: user A creates a household and invites B; B accepts. Using the
   sample item fixture (`uv run python manage.py ascua_demo_items`, development only), A shares
   item 1 as visible and item 2 as editable. B can read 1 and edit 2; B cannot see A's private
   item 3. A sets item 2 to 50/50 with B → B sees an offer and accepts → each sees a 50% share.
6. **Viewer (US5)**: A adds V as household viewer → V sees items 1 and 2 read-only; edits are
   refused.
7. **Support access (US6)**: A grants 1 hour; admin D reads A's profile under `/support/A/…`; A's
   access log shows `support.viewed` within 1 minute. A revokes → D gets 404.
8. **Export (US7)**: A requests an export → notification when ready → ZIP contains `export.json`
   (`format_version: 1`) and CSVs, with no secrets.
9. **Deletion blockers (US7)**: A (household owner, co-owner of item 2) requests deletion → blocked
   with both reasons listed. A transfers ownership to B and relinquishes the item 2 share →
   deletion succeeds, all A's sessions end, and A's email no longer signs in.

## Expected outcomes

All automated checks pass, and each manual scenario behaves as described with no data from another
user visible at any step.
