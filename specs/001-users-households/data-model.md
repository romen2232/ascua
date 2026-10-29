# Data Model: Users, Households and Data Isolation

**Feature**: 001-users-households | **Date**: 2026-10-29 | **Plan**: [plan.md](plan.md)

Conventions: primary keys are UUIDv7 (time-ordered, not guessable); timestamps are UTC
`timestamptz`; dates are ISO 8601; percentages are integer basis points (bp, 10,000 = 100%); money is
integer cents. **RLS** names the row-level security rule applied (see research R2/R3). "Owner"
below means the tenant owner used by RLS, not necessarily an ownership share.

## accounts app

### User

| Field | Type | Rules |
| --- | --- | --- |
| id | uuid | |
| email | citext, unique | Normalised lower-case |
| display_name | text ≤ 80 | |
| password | text, nullable | Argon2id hash; null for provider-only users |
| language | enum `es`, `en` | Default from invitation or `es` |
| is_admin | bool | Instance admin flag |
| status | enum | See state machine |
| disclaimer_accepted_at | timestamptz, nullable | FR-013 |
| created_at, last_login_at | timestamptz | |

State machine: `pending_mfa` → `active` (TOTP confirmed, or first provider sign-in);
`active` ↔ `disabled` (admin); `active` → `mfa_reset_required` → `active` (two-factor reset);
any → deleted (row removed). Only `active` users can obtain tokens; `pending_mfa` and
`mfa_reset_required` can only reach the two-factor setup endpoints.

RLS: none on the table itself. Admins read only metadata columns, through a dedicated serializer.
The user reads their own row.

### ExternalIdentity

`id`, `user` → User, `issuer` text, `subject` text, `email_at_link` text, `linked_at`.
Unique (`issuer`, `subject`). One per user per issuer.

### Invitation

| Field | Type | Rules |
| --- | --- | --- |
| id | uuid | |
| email | citext | |
| token_hash | bytea, unique | SHA-256 of the random token in the link |
| invited_by | → User | Admin, or household owner for household invitations |
| household | → Household, nullable | Household invitation if set |
| household_role | enum `member`, `viewer`, nullable | Required if `household` set |
| grants_admin | bool | Only from `ascua_init` or an admin |
| expires_at | timestamptz | Default now + 7 days (FR-003) |
| used_at, revoked_at | timestamptz, nullable | Single use |

A valid invitation is not used, not revoked and not expired. Instance invitations (no household)
create accounts. Household invitations to an existing user are accepted in-app; to an unknown email
they also create the account (still subject to FR-002).

### InstanceSettings (singleton)

`open_registration` bool (default false), `oidc_enabled` bool (derived from env config, read-only),
`email_enabled` bool (derived), `updated_at`.

### DeviceSession

`id` (the `sid` JWT claim), `user`, `device_name` text, `user_agent` text, `created_at`,
`last_used_at`, `absolute_expires_at` (= created + 90 d), `revoked_at`.
Active ⇔ not revoked ∧ now < `last_used_at` + 30 d ∧ now < `absolute_expires_at`. RLS: owner = user.

### PersonalAccessToken

`id`, `user`, `name` ≤ 60, `prefix` (first 8 characters, for display), `token_hash` bytea unique,
`scope` enum `read` | `read_write`, `expires_at` (required, ≤ 1 year), `last_used_at`,
`revoked_at`, `created_at`. RLS: owner = user.

### MFA devices (django-otp)

`TOTPDevice` and `StaticDevice` (10 recovery codes, each single use), owned by the user.
Not exposed except via setup and verify endpoints. Included in deletion, not in export (secrets).

## profiles app

### TaxProfile (one per user)

| Field | Type | Rules |
| --- | --- | --- |
| user | → User, PK | |
| birth_date | date, nullable until completed | Not in the future; age ≤ 120 |
| employment_type | enum `employee`, `autonomo`, `none` | |
| completed_at | timestamptz, nullable | Set when all required fields present |
| version | int | Optimistic concurrency |

RLS: owner = user; support mode read for subject.

### RegionResidence

`id`, `profile` → TaxProfile, `region_code` text (INE code from `rules/ES/regions.yaml`, validated
at write time), `effective_from` date. Unique (`profile`, `effective_from`). The current region is
the row with the latest `effective_from` ≤ today; the region for tax year Y is the residence on
31 December of Y. At least one row once the profile is completed.

### Dependant

`id`, `profile`, `relationship` enum `descendant` | `ascendant`, `birth_year` int (1900–current),
`disability_percent` int 0–100 (Spanish tax thresholds 33 and 65 are applied later by rule packs),
`cohabits` bool, `label` text ≤ 40 (optional nickname). The relationship field is added because
Spanish family minimums differ for descendants and ascendants.

### SocialSecuritySummary (one per profile, optional)

`profile` PK, `first_contribution_date` date nullable, `years_contributed` decimal(4,2) 0–60,
`current_regime` enum `general` | `autonomos` | `other` | `none`, `updated_at`.

## households app

### Household

`id`, `name` ≤ 80, `owner` → User (always also a membership with role `owner`), `created_at`,
`version`. Invariant: exactly one owner (FR-027).

### HouseholdMembership

`id`, `household`, `user` **unique** (at most one household per user, FR-022), `role` enum
`owner` | `member` | `viewer`, `joined_at`. Unique partial index: one `owner` row per household.

Transitions: invitation accepted → membership created; owner transfer swaps roles atomically;
leave or removal deletes the row and, in the same transaction, revokes that user's
`SharingSetting` rows for the household. The owner can delete the household only when they are the
sole member.

### HouseholdGoal

`id`, `household`, `name` ≤ 80, `target_amount_cents` bigint ≥ 0, nullable, `target_date` date,
nullable, `notes` text ≤ 500, `version`. Editable by the owner only; readable by all members and
viewers.

RLS for household tables: readable by any membership of that household; writable per role.

## sharing app

### Item

`id`, `kind` text (e.g. `account`, registered by later features), `created_by` → User,
`created_at`, `version`. Concrete entities in later specs reference it with a one-to-one key.

### OwnershipShare

| Field | Type | Rules |
| --- | --- | --- |
| id | uuid | |
| item | → Item | |
| user | → User, nullable | Null ⇒ external owner |
| external_label | text ≤ 60, nullable | Required when `user` is null |
| share_bp | int 1–10000 | |
| status | enum `accepted`, `pending` | External shares are always `accepted` |
| offered_by | → User, nullable | For pending shares |
| offered_at, responded_at | timestamptz | |

Invariants (deferred constraint trigger, checked at commit):
- Σ `share_bp` over all rows of an item = 10,000.
- At most one row per (item, user).
- At least one `accepted` user owner exists, so the item always has someone who can manage it.

Pending share lifecycle: `pending` → `accepted` (recipient accepts; recipient now sees the item) or
→ declined (row converted to an external share labelled "Declined share" with the same `share_bp`,
and the offering owner gets a notification). Shares counted in personal and household figures:
`accepted` rows with a user only.

Changing shares (FR-019): reducing user X's share requires X to be the actor or to have agreed
through an `OwnershipChangeRequest`. Giving user Y a new or larger share creates or updates Y's row
as `pending` for the added amount.

### OwnershipChangeRequest

`id`, `item`, `requested_by`, `proposed` jsonb (the full target share list), `approvals` jsonb
(user ids required and given), `status` enum `open` | `applied` | `rejected` | `superseded`,
`created_at`. Created when a change reduces another user owner's share; applied automatically once
every affected owner approves. Opening a new request supersedes the previous open one for that item.

### SharingSetting

`id`, `item`, `household`, `level` enum `visible` | `editable` (a missing row means private, the
default), `included_in_totals` bool (set by the household owner, default false), `set_by` → User,
`updated_at`. Unique (`item`, `household`). Only accepted user owners who are members (not viewers)
of that household may create or change it (FR-020, FR-023).

### ViewerGrant

`id`, `grantor` → User, `viewer` → User (≠ grantor), `ends_at` timestamptz nullable,
`revoked_at`, `created_at`. `ViewerGrantItem`: (`grant`, `item`), where the grantor must be an
accepted owner of the item. Active ⇔ not revoked ∧ (`ends_at` null ∨ now < `ends_at`).

### Access rules (implemented in `ascua.can_read_item` / `ascua.can_write_item`)

Actor A can **read** item I if any of:
1. A holds an `accepted` share in I;
2. A holds a `pending` share in I: A sees only the offer summary (name, kind, offered share), not
   the item's data;
3. I has a `SharingSetting` for A's household (A is owner, member or viewer there);
4. an active `ViewerGrant` to A includes I;
5. support mode with `subject_id` = U and U satisfies rule 1.

A can **write** item data if rule 1 holds, or rule 3 holds with `level = editable` and A's role is
`owner` or `member`. Only rule-1 owners can change ownership or sharing.

Household totals (FR-025): for items with `included_in_totals`, the sum over `accepted` shares whose
user is the household's owner or a member. Viewers' shares and external shares are excluded.

## support app

### SupportGrant

`id`, `user` (subject), `starts_at`, `ends_at` (≤ starts + 7 days, default + 24 h), `revoked_at`,
`expiry_logged` bool. Active ⇔ not revoked ∧ `starts_at` ≤ now < `ends_at`. At most one active grant
per user; a new grant replaces the old one. A beat task (every minute) writes an `expired` log entry
for grants that have just ended, which satisfies SC-006.

### AccessLogEntry (append-only)

`id`, `subject` → User (the affected user, who can see the entry), `actor` → User, nullable
(null = system), `action` enum (`support.granted`, `support.revoked`, `support.expired`,
`support.viewed`, `admin.invited`, `admin.disabled`, `admin.enabled`, `admin.mfa_reset_requested`,
`admin.mfa_reset`, `admin.appointed`, `admin.revoked`), `target` text (e.g. the resource path
viewed), `created_at`. RLS: subject reads own entries; inserts only via functions; no update or
delete (R12).

## privacy app

### ExportJob

`id`, `user`, `status` enum `queued` | `running` | `ready` | `failed` | `expired`, `file_path`
(private storage), `size_bytes`, `format_version` int, `requested_at`, `ready_at`, `expires_at`
(ready + 7 days). RLS: owner = user.

## notifications app

### Notification

`id`, `user`, `kind` enum (`share.offered`, `share.declined`, `ownership.change_requested`,
`household.invited`, `export.ready`, `support.expired`, …), `payload` jsonb (ids and display text
only), `created_at`, `read_at`. RLS: owner = user. Included in export and deletion.

## Coverage check

Every tenant table above must appear in (a) an RLS policy migration, (b) an export section or a
documented exclusion (MFA secrets, token hashes), (c) a deletion handler or `ON DELETE CASCADE`, and
(d) the database-level isolation test. A test enumerates Django models and fails on any gap.
