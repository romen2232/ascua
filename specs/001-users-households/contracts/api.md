# API Contract: Users, Households and Data Isolation

**Feature**: 001-users-households | **Base path**: `/api/v1` | **Format**: JSON, UTF-8

The OpenAPI 3 document is generated from code by drf-spectacular at `/api/v1/schema/`; this file is
the reviewed inventory it must match (checked by a contract test). Field details live in
[data-model.md](../data-model.md).

## Conventions

- **Auth**: `Authorization: Bearer <access JWT>` or `Bearer ascua_pat_…` (personal access token).
  "Anon" = no auth. "MFA" = the short-lived `mfa_token` from step 1 of sign-in or sign-up.
- **Errors**: `{"code": "<stable_code>", "detail": "<translated message>", "fields": {…}}`.
  `detail` follows `Accept-Language` (`es`, `en`). Clients branch on `code`, never on `detail`.
- **Not found vs. forbidden**: any resource the actor cannot read returns `404 not_found`, the same
  as a non-existent id (FR-015). `403` is used only when the actor can read but not write.
- **Concurrency**: editable resources return `ETag`; `PATCH` requires `If-Match` →
  `412 version_conflict` on mismatch; `428 if_match_required` if the header is missing.
- **Pagination**: cursor-based, `?cursor=…&page_size=` (≤ 100), response
  `{"results": [...], "next": "…" | null}`.
- **Rate limits**: auth endpoints are throttled; `429 throttled` with `Retry-After`.
- **PAT scope**: `read` tokens get `403 token_scope` on any non-GET request. PATs cannot call
  `/auth/*`, `/me/tokens`, `/me/sessions`, `/me/delete` or `/admin/*`.
- **Isolation**: every authenticated route is listed in `tests/isolation/registry.py`
  ([isolation.md](isolation.md)).

## Authentication and sign-up

| Method | Path | Auth | Purpose | Success | Notable errors |
| --- | --- | --- | --- | --- | --- |
| GET | `/auth/invitations/{token}` | Anon | Check an invitation; returns email, household name if any, expiry | 200 | 404 `invitation_invalid` (expired, used, revoked or unknown, all the same) |
| POST | `/auth/signup` | Anon | `{invitation_token \| null, email, password, display_name, language}`; creates a `pending_mfa` user | 201 `{mfa_token, totp: {secret, otpauth_uri}}` | 400 `password_policy`, 403 `registration_closed`, 404 `invitation_invalid` |
| POST | `/auth/mfa/setup/confirm` | MFA | `{code}` confirms TOTP; activates user, consumes invitation | 200 `{access, refresh, recovery_codes[10]}` | 400 `mfa_code_invalid` |
| POST | `/auth/login` | Anon | `{email, password, device_name}` | 200 `{mfa_token}`; for `mfa_reset_required`: `{mfa_token, totp_setup_required: true}` | 401 `credentials_invalid`, 429 |
| POST | `/auth/login/mfa` | MFA | `{code}` (TOTP or recovery code) | 200 `{access, refresh}` | 400 `mfa_code_invalid`, 429 |
| POST | `/auth/token/refresh` | Anon (refresh in body) | Rotate tokens; enforces 30-day idle / 90-day absolute limits | 200 `{access, refresh}` | 401 `session_expired` |
| POST | `/auth/logout` | Bearer | End the current session | 204 | |
| GET | `/auth/oidc/start` | Anon | `?invitation=<token>` optional; 302 to the provider | 302 | 404 `oidc_disabled` |
| GET | `/auth/oidc/callback` | Anon | Provider callback; 302 to `ascua://auth/callback?code=…` or `?error=…` | 302 | |
| POST | `/auth/oidc/exchange` | Anon | `{code, device_name}` (single use, 60 s) | 200 `{access, refresh}` | 400 `oidc_code_invalid`, 403 `oidc_not_linked` |
| POST | `/auth/reauth` | Bearer | `{password, code}` or `{oidc_code}`; returns a 5-minute `reauth_token` for destructive actions | 200 `{reauth_token}` | 401 |
| POST | `/auth/mfa/reset/confirm` | Anon | `{token}` from the email the admin's reset triggered | 204 | 404 |

## Current user

| Method | Path | Purpose | Notes |
| --- | --- | --- | --- |
| GET, PATCH | `/me` | Display name, language, email (read-only), status | |
| POST | `/me/disclaimer` | Acknowledge the disclaimer (FR-013) | Idempotent |
| GET | `/me/sessions` | List device sessions | |
| DELETE | `/me/sessions/{id}` | End a session | Effective immediately |
| GET, POST | `/me/tokens` | List or create PATs `{name, scope, expires_at}`; the secret is returned once | 400 if expiry > 1 year |
| DELETE | `/me/tokens/{id}` | Revoke a PAT | |
| GET | `/me/notifications` | List; `?unread=true` | |
| POST | `/me/notifications/{id}/read` | Mark read | |

## Tax profile

| Method | Path | Purpose |
| --- | --- | --- |
| GET, PATCH | `/me/profile` | `birth_date`, `employment_type`, `current_region` (read-only), `completed` |
| GET, POST | `/me/profile/regions` | Region history; POST `{region_code, effective_from}` |
| PATCH, DELETE | `/me/profile/regions/{id}` | Cannot delete the only row |
| GET, POST | `/me/profile/dependants` | |
| PATCH, DELETE | `/me/profile/dependants/{id}` | |
| GET, PUT | `/me/profile/social-security` | Summary |
| GET | `/reference/regions` | Region list from the rule pack, translated `name`, `regime`, `rules_supported` |

Validation codes: `birth_date_future`, `birth_date_too_old`, `region_unknown`,
`effective_from_duplicate`, `years_contributed_range`.

## Households

| Method | Path | Role | Purpose |
| --- | --- | --- | --- |
| POST | `/households` | Not in a household | Create; caller becomes owner. 409 `already_in_household` |
| GET | `/households/current` | Any member | Household, members, caller's role |
| PATCH | `/households/current` | Owner | Rename |
| DELETE | `/households/current` | Owner, sole member | Dissolve. 409 `household_has_members` |
| POST | `/households/current/invitations` | Owner | `{email, role}`; existing users get an in-app invitation, others an instance invitation |
| GET | `/households/invitations` | Invitee | Pending household invitations for the caller |
| POST | `/households/invitations/{id}/accept`, `/decline` | Invitee | 409 `already_in_household` |
| PATCH | `/households/current/members/{user_id}` | Owner | `{role}` (`member`, `viewer`) |
| DELETE | `/households/current/members/{user_id}` | Owner, or self to leave | Owner leaving gets 409 `owner_must_transfer` |
| POST | `/households/current/transfer` | Owner | `{user_id}` of a member |
| GET, POST | `/households/current/goals` | Read: all; write: owner | |
| PATCH, DELETE | `/households/current/goals/{id}` | Owner | |
| GET | `/households/current/items` | Any member | Items shared with the household, level, `included_in_totals`, and the members' combined `share_bp` |
| PATCH | `/households/current/items/{item_id}` | Owner | `{included_in_totals}` |

## Ownership and sharing (generic over items)

Later features expose items under their own routes (e.g. `/accounts/{id}`); these routes manage
ownership and sharing for any item.

| Method | Path | Who | Purpose |
| --- | --- | --- | --- |
| GET | `/items/{id}/ownership` | Readers | Shares with status; pending offers visible to owners and to the recipient |
| PUT | `/items/{id}/ownership` | Accepted owner | Full target list `[{user_id \| external_label, share_bp}]`. Applied at once if no other user owner loses share (new or increased shares become `pending`); otherwise returns 202 with an `OwnershipChangeRequest`. 400 `shares_must_total_100` |
| GET | `/ownership-requests` | Involved owners | Open change requests |
| POST | `/ownership-requests/{id}/approve`, `/reject` | Affected owner | |
| GET | `/share-offers` | Recipient | Pending offers made to the caller |
| POST | `/share-offers/{id}/accept`, `/decline` | Recipient | Decline converts to external share and notifies the offerer |
| POST | `/items/{id}/ownership/relinquish` | Accepted owner | `{to: "co_owners" \| "external", external_label?}`; never needs approval (FR-034) |
| GET, PUT | `/items/{id}/sharing` | Accepted owner and household member | `{level: "private" \| "visible" \| "editable"}` |
| GET, POST | `/viewer-grants` | Grantor | `{viewer_email, item_ids[], ends_at?}`; the viewer must be a user of the instance (404 otherwise, without revealing whether the email exists) |
| DELETE | `/viewer-grants/{id}` | Grantor | Revoke |
| GET | `/viewer-grants/received` | Viewer | Grants received |

## Support access

| Method | Path | Who | Purpose |
| --- | --- | --- | --- |
| GET | `/me/support-grant` | User | Current grant or null |
| POST | `/me/support-grant` | User | `{duration_hours}` 1–168, default 24 |
| DELETE | `/me/support-grant` | User | Revoke |
| GET | `/me/access-log` | User | Own log entries, newest first |
| GET | `/support/{user_id}/profile` and `/support/{user_id}/…` read mirrors of user routes | Admin with active grant from that user | Read-only transaction; every call logged. 404 without a grant |

## Instance administration (no financial data)

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/admin/users` | Metadata only: name, email, status, admin flag, created, last sign-in, `support_grant_active` |
| PATCH | `/admin/users/{id}` | `{status: active \| disabled}`; `{is_admin}` (cannot remove the last admin) |
| POST | `/admin/users/{id}/mfa-reset` | Emails the user a confirmation link; 409 `email_disabled` without SMTP (operator uses the CLI) |
| GET, POST | `/admin/invitations` | List or create `{email, grants_admin?}`; response includes the link to copy |
| DELETE | `/admin/invitations/{id}` | Revoke |
| GET, PATCH | `/admin/settings` | `{open_registration}` |

## Privacy

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/me/exports` | Queue an export → 202 `{id, status}`; one running at a time (409) |
| GET | `/me/exports` | List with status and expiry |
| GET | `/me/exports/{id}/download` | Streams the ZIP; owner only; 410 `export_expired` |
| GET | `/me/delete/check` | Blockers: `{blockers: [{code: "household_owner" \| "co_owned_items" \| "last_admin", items?: [...]}]}` |
| POST | `/me/delete` | `{reauth_token, confirm: "DELETE"}`; 409 with blockers if any remain; 204 then all sessions end |

## CLI (operator)

| Command | Purpose |
| --- | --- |
| `manage.py ascua_init` | First run: creates settings and an admin invitation, prints the link; refuses if users exist |
| `manage.py ascua_reset_mfa <email>` | Operator two-factor reset when email is unavailable; logged as `admin.mfa_reset` |
| `manage.py ascua_demo_items <email>` | Development only (`DEBUG=True`): creates three sample items for manual sharing checks until spec 002 adds accounts |
