# Feature Specification: Users, Households and Data Isolation

**Feature Branch**: `001-users-households`

**Created**: 2026-10-29

**Status**: Draft

**Input**: User description: "Spec 001 from requirements.md Phase 1: USR-1 to USR-6, NF-2, NF-3, NF-6 —
individual tax profiles, ownership shares, households and item-level sharing, admin support access,
invitation-based sign-up, strong authentication, cross-user isolation, and GDPR export and deletion."

**Requirement traceability**: USR-1, USR-2, USR-3, USR-4, USR-5, USR-6, NF-2, NF-3, NF-6.
Out of scope here: USR-7 (dependant profiles), NF-5 full audit log (only support-access logging is
covered), TAX-7 joint filing.

## Clarifications

### Session 2026-10-29

- Q: Should two-factor authentication be mandatory for every user, or optional unless the admin
  enforces it? → A: Mandatory for everyone, set up during sign-up and impossible to turn off;
  users who sign in through an external identity provider are exempt because the provider handles
  it.
- Q: When a user lists another user as co-owner of an item, must that person accept before it
  appears in their data and totals? → A: Yes. Until accepted, the share is pending and counts
  towards nobody; this includes shares handed over by a departing co-owner, and a declined share
  goes to an external owner.
- Q: What can a household viewer see? → A: Read-only access to every item shared with the
  household (visible or editable) and to household totals and goals; their own items never count
  towards household totals and they cannot share items into the household.
- Q: Should a user be able to import their own ascua export back in? → A: Not in this feature. The
  export uses a documented, versioned format so a later feature can add import; this feature only
  guarantees the export is complete.
- Q: How long should a mobile sign-in last before the user must enter their password and one-time
  code again? → A: Sessions expire after 30 days without use and 90 days at most; the app requires
  the device's biometric or PIN unlock on every open after 5 minutes in the background.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Invited sign-up and secure sign-in (Priority: P1)

The instance admin invites a person by email. The person opens the invitation, creates an account
with a strong password, sets up a two-factor authenticator, and from then on signs in with both.
Nobody can sign up without an invitation unless the admin deliberately turns open registration on.
Where the admin has connected an external identity provider, people can sign in through it instead.

**Why this priority**: nothing else in ascua is usable or safe without accounts and authentication.

**Independent Test**: on a fresh instance, the admin invites one person; that person completes
sign-up and two-factor setup and signs in; an uninvited person cannot register.

**Acceptance Scenarios**:

1. **Given** a fresh instance, **When** the first-run setup completes, **Then** exactly one instance
   admin exists and open registration is disabled.
2. **Given** open registration is disabled, **When** someone without a valid invitation tries to
   sign up, **Then** sign-up is refused and no account is created.
3. **Given** a valid, unexpired invitation, **When** the invitee chooses a password that meets the
   password policy and completes two-factor setup, **Then** the account is created and the
   invitation can no longer be used; sign-up cannot finish without two-factor setup.
4. **Given** an expired or already-used invitation, **When** it is opened, **Then** sign-up is
   refused with an explanation.
5. **Given** a user who signs in with a password, **When** they enter a correct password but a
   wrong or missing one-time code, **Then** sign-in fails.
6. **Given** the admin has configured an external identity provider, **When** an invited person
   signs in through it, **Then** they are linked to their ascua account and signed in without an
   ascua one-time code.
7. **Given** repeated failed sign-in attempts on one account, **When** a threshold is passed,
   **Then** further attempts are throttled.
8. **Given** a mobile session unused for 30 days, or 90 days old, **When** the app is opened,
   **Then** the user must sign in again in full; **Given** the app was in the background for more
   than 5 minutes, **When** it is reopened, **Then** the device's biometric or PIN unlock is
   required before any data is shown.
9. **Given** a signed-in user, **When** they create a personal access token with a name and expiry,
   **Then** the token is shown once, can be used for scripted access to their own data only, and can
   be revoked at any time.

---

### User Story 2 - Individual tax profile (Priority: P1)

Each user records the personal facts that Spanish tax and pension calculations depend on: birth
date, autonomous community of tax residence, employment type (employee, autónomo, none),
dependants, and a summary of their Social Security history.

**Why this priority**: every later calculation (IRPF, pension, FIRE ages) reads this profile.

**Independent Test**: a user completes their profile, edits it, and sees it saved; invalid values
are rejected.

**Acceptance Scenarios**:

1. **Given** a new user, **When** they first sign in, **Then** they are asked to complete their tax
   profile and see the disclaimer that ascua is an educational simulation, not advice.
2. **Given** the profile form, **When** the user selects a region, **Then** only the 17 autonomous
   communities plus Ceuta and Melilla are offered, with Navarra and the Basque Country labelled as
   foral regimes that may lack rule support.
3. **Given** a birth date in the future or implying an age over 120, **When** saved, **Then** it is
   rejected.
4. **Given** the user adds dependants (birth year, disability degree if any, cohabitation),
   **When** saved, **Then** they appear in the profile.
5. **Given** the user enters a Social Security summary (date of first contribution, years
   contributed, current regime), **When** saved, **Then** it is stored for later pension estimates.
6. **Given** a user changes their region, **When** saved, **Then** the change records the date it
   took effect, so earlier tax years keep the earlier region.

---

### User Story 3 - Strict separation between users (Priority: P1)

Several people share one instance. Each user only ever sees their own data and what has been
explicitly shared with them. The instance admin manages the server but cannot see anyone's
finances.

**Why this priority**: a leak between users on a shared server defeats the product's purpose
(Constitution Principle II).

**Independent Test**: with two users and one admin, every read and write operation attempted by
one party against another's data is refused, through the app and through the API.

**Acceptance Scenarios**:

1. **Given** users A and B with no sharing, **When** A requests any of B's records by any means
   (listing, direct identifier, search, export, aggregate), **Then** nothing of B's is returned and
   the response does not reveal whether the record exists.
2. **Given** the instance admin with no support grant, **When** they browse users, **Then** they see
   account metadata (name, email, status, sign-in dates) but no profile, financial or household data.
3. **Given** a personal access token for user A, **When** it is used, **Then** it reaches only data
   A could reach in the app.
4. **Given** any data-access operation added in this or a later feature, **When** the test suite
   runs, **Then** an automated test proves another user, another household's member and an
   ungranted admin are all denied.

---

### User Story 4 - Households and item-level sharing (Priority: P2)

A user creates a household and invites their partner. Each member decides, account by account,
whether it is private, visible to the household, or editable by the household. The household owner
chooses which shared items count toward the household's combined figures. A jointly held account
records each owner's share, for example 50/50, so each person's tax uses their own part.

**Why this priority**: households are central to planning FIRE together, but individual use works
without them.

**Independent Test**: two users form a household, one shares an account as visible and another as
editable, and the other member can read the first and edit the second but cannot see a private one.

**Acceptance Scenarios**:

1. **Given** a user not in a household, **When** they create one, **Then** they become its owner.
2. **Given** a household owner, **When** they invite an existing user or an email address, **Then**
   the invitee joins only after accepting, with the role chosen by the owner (member or viewer).
3. **Given** a new item, **When** it is created, **Then** its sharing level is private.
4. **Given** an item shared as visible, **When** another member opens it, **Then** they can read but
   not change it; **Given** editable, **Then** they can change its data but not its sharing level or
   ownership.
5. **Given** an item co-owned by A (60%) and B (40%), **When** ownership is saved, **Then** shares
   must total exactly 100%, and each owner's personal totals include only their share.
6. **Given** A lists B as 40% co-owner of A's account, **When** B has not yet responded, **Then**
   B cannot see the account and the 40% counts towards nobody's totals; **When** B accepts, **Then**
   the account appears in B's data with 40%; **When** B declines, **Then** the 40% passes to an
   external owner and A is told.
7. **Given** a household with included items, **When** combined figures are shown, **Then** each
   item contributes the sum of the ownership shares held by the household owner and members (not
   viewers), and excluded or private items contribute nothing.
8. **Given** a member who leaves or is removed, **When** this happens, **Then** their items stop
   being visible to the household immediately, and items they co-own with remaining members stay
   visible to those co-owners.
9. **Given** a household owner who wants to leave, **When** other members remain, **Then** they must
   first transfer ownership to another member.

---

### User Story 5 - Viewers: read-only access for a partner or adviser (Priority: P3)

A user grants a trusted person, such as an adviser, read-only access to selected items, optionally
until a date. Separately, a household owner can add someone with the household viewer role, who
then reads everything shared with the household (FR-023).

**Why this priority**: useful but not needed for the core household flow.

**Independent Test**: a user grants a viewer access to one account; the viewer can read only that
account and loses access when it is revoked or expires.

**Acceptance Scenarios**:

1. **Given** a user grants viewer access to specific items, **When** the viewer signs in, **Then**
   they see only those items, read-only.
2. **Given** a grant with an end date, **When** the date passes, **Then** access ends automatically.
3. **Given** a viewer, **When** they try any change, **Then** it is refused.
4. **Given** a household viewer, **When** they open the household, **Then** they see every item
   shared with it (visible or editable) plus household totals and goals, read-only, and none of the
   members' private items; the viewer's own items do not appear in household totals.

---

### User Story 6 - Time-limited support access (Priority: P2)

A user who needs help from the instance admin grants support access for a limited time. The admin
can then see that user's data read-only, and every access is logged where the user can see it.

**Why this priority**: lets self-hosters help family members without weakening the default privacy.

**Independent Test**: a user grants 1 hour of support access; the admin can read the user's data
during the hour, cannot after it, and the user sees each access in their log.

**Acceptance Scenarios**:

1. **Given** a user, **When** they grant support access, **Then** they choose a duration (up to 7
   days, default 24 hours) and can revoke it at any time.
2. **Given** an active grant, **When** the admin views that user's data, **Then** access is
   read-only and each view is logged with time and what was viewed.
3. **Given** an expired or revoked grant, **When** the admin tries to view the data, **Then** access
   is refused.
4. **Given** a user, **When** they open their access log, **Then** they see grant, revoke, expiry
   and every admin access event, and these entries cannot be edited or deleted by anyone.

---

### User Story 7 - Export my data and delete my account (Priority: P2)

A user downloads everything ascua holds about them, in machine-readable and spreadsheet-friendly
formats, and can permanently delete their account and data.

**Why this priority**: a legal right under GDPR and a trust requirement for a self-hosted tool.

**Independent Test**: a user with profile, household and shared data exports it and gets complete
files; then deletes their account and can no longer sign in, with their data gone.

**Acceptance Scenarios**:

1. **Given** a user, **When** they request an export, **Then** they receive an archive with all
   their data in JSON and CSV, including profile, ownership shares, sharing settings, household
   memberships and access log, and nothing belonging only to other users.
2. **Given** an export request, **When** it is large, **Then** it is prepared in the background and
   the user is told when it is ready; the download link works only for that user and expires.
3. **Given** a user requests account deletion, **When** they re-authenticate (password and
   one-time code, or a fresh sign-in through their external identity provider), **Then** their
   account and personal data are deleted and they are signed out everywhere.
4. **Given** the user owns a household with other members, **When** they request deletion, **Then**
   they must first transfer household ownership.
5. **Given** the user co-owns items with other users, **When** they delete their account, **Then**
   deletion is blocked and the user is shown every co-owned item; for each one they must first give
   up their share (to the remaining co-owners or to an external owner), after which deletion can
   proceed.
6. **Given** the instance's only admin, **When** they request deletion, **Then** it is refused until
   another admin exists.

---

### Edge Cases

- A user is invited to a second household while already in one: a user belongs to at most one
  household at a time, so they must leave their current household before accepting; read-only
  access to another household's items is possible through viewer grants (FR-028).
- Ownership shares that do not total 100%, negative shares, or a co-owner who is not a user of this
  instance (e.g. a sibling without an account): the remainder is held by an "external owner" that
  counts towards nobody's totals.
- Item editable by the household, and a member tries to change its owners or sharing level: refused.
- Support access requested while the user is a viewer elsewhere: the admin sees only that user's own
  data, never items merely granted to them.
- Lost two-factor device: recovery codes generated at setup allow one-time sign-in; without them, the
  admin can reset two-factor only after the user confirms by email, and the reset is logged. After a
  reset the user must set up two-factor again before reaching any data.
- A user who signs in through an external identity provider is unlinked from it, or the admin
  disconnects the provider: affected users must set a password and set up two-factor at their next
  sign-in.
- Admin disables open registration while invitations are outstanding: existing invitations remain
  valid until they expire.
- Email delivery not configured on the instance: the admin can copy an invitation link to send by
  other means.
- Concurrent edits to an editable shared item: the later save is refused if the item changed since
  it was loaded, and the user is asked to reload.

## Requirements *(mandatory)*

### Functional Requirements

**Accounts and authentication (NF-2, USR-6)**

- **FR-001**: The first-run setup MUST create exactly one instance admin; further admins can be
  appointed by an existing admin.
- **FR-002**: Sign-up MUST require a valid, single-use invitation by default; open registration MUST
  be off by default and only an admin can enable it.
- **FR-003**: Invitations MUST expire (default 7 days) and can be revoked by the admin before use.
- **FR-004**: Passwords MUST be stored only as salted hashes using a memory-hard algorithm, and MUST
  meet a minimum length of 12 characters and be checked against a list of common passwords.
- **FR-005**: Every user who signs in with a password MUST set up time-based one-time-code
  two-factor authentication during sign-up and MUST NOT be able to disable it; they receive
  single-use recovery codes at setup. Users who sign in only through an external identity provider
  (FR-006) are exempt, since that provider is responsible for their second factor.
- **FR-006**: The admin MAY connect an external identity provider using a standard protocol; when
  connected, invited users can sign in through it.
- **FR-007**: Repeated failed sign-ins MUST be throttled per account and per source.
- **FR-008**: Users MUST be able to see and end their active sessions and devices.
- **FR-008a**: A session MUST expire after 30 days without use and in any case 90 days after
  sign-in, after which the user signs in again in full. The mobile app MUST require the device's
  biometric or PIN unlock whenever it is opened after more than 5 minutes in the background; if the
  device has no lock configured, the app MUST ask the user to set one before showing any data.
  Personal access tokens follow their own expiry (FR-009), not these limits.
- **FR-009**: Users MUST be able to create, name, list and revoke personal access tokens with an
  expiry date; a token's permissions never exceed its owner's.

**Tax profile (USR-1)**

- **FR-010**: Each user MUST have one tax profile with birth date, region of tax residence (with
  effective-from date), employment type (employee, autónomo, none), dependants and a Social Security
  summary.
- **FR-011**: The region list MUST come from rule-pack configuration, not be fixed in the app.
- **FR-012**: Each user MUST be able to set their language (Spanish or English); all screens and
  messages in this feature MUST be available in both.
- **FR-013**: On first sign-in each user MUST see and acknowledge the disclaimer that ascua is an
  educational simulation, not financial, tax or legal advice.

**Isolation (NF-3, USR-5)**

- **FR-014**: Every record holding personal or financial data MUST belong to a user or a household,
  and access to it MUST be decided by that ownership plus explicit sharing, enforced for every access
  path (app, API, exports, background jobs).
- **FR-015**: Denied access MUST be indistinguishable from a non-existent record.
- **FR-016**: Instance admins MUST NOT access users' profile, financial or household data except
  through an active support grant (FR-030).
- **FR-017**: Every data-access operation MUST have automated tests proving that another user,
  a member of another household, and an ungranted admin are denied.

**Ownership and sharing (USR-2, USR-4)**

- **FR-018**: Each shareable item MUST have one or more owners with percentage shares totalling
  exactly 100%, to two decimal places; part of the share MAY be held by an external (non-user) owner.
- **FR-019**: Only owners MAY change an item's ownership. Reducing a user owner's share requires
  that owner's agreement; giving a user a new or larger share requires that user's acceptance.
  Until accepted, the offered share is pending: it counts towards nobody's totals and the recipient
  cannot see the item. A declined share passes to an external owner and the offering owner is
  notified. External owners never need to accept.
- **FR-020**: Each item MUST have a sharing level per household: private (default), visible or
  editable; only its user owners MAY change it.
- **FR-021**: Each personal figure MUST count only the user's own share of each item.

**Households (USR-3)**

- **FR-022**: A user MAY create a household and becomes its owner. A user MUST belong to at most
  one household at a time.
- **FR-023**: Household roles MUST be owner, member and viewer, with the permissions in the
  requirements' role table. A household viewer MUST have read-only access to every item shared with
  the household (visible or editable) and to household totals and goals, and nothing else of other
  members. A viewer MUST NOT share their own items into the household, and their items never count
  towards household totals. Viewer membership counts as the user's one household (FR-022).
- **FR-024**: The owner MUST be able to invite and remove members, change roles, set shared goals, and
  choose which shared items count toward household totals.
- **FR-025**: Household totals MUST include, for each included item, the sum of the shares held by
  household owner and members (not viewers), and nothing from private or excluded items.
- **FR-026**: When a member leaves or is removed, the household MUST lose access to their items at
  once; their own data is unaffected.
- **FR-027**: A household MUST always have exactly one owner; the owner can leave only after transfer,
  or by dissolving a household with no other members.

**Viewers (USR-4)**

- **FR-028**: A user MAY grant read-only viewer access to specific items to another user of the
  instance, optionally with an end date, and revoke it at any time.

**Support access (USR-5)**

- **FR-029**: Admin actions on user accounts (invite, disable, two-factor reset, admin appointment)
  MUST be logged.
- **FR-030**: A user MAY grant the admins read-only support access to their own data for a chosen
  duration (default 24 hours, maximum 7 days), revocable at any time.
- **FR-031**: Grants, revocations, expiries and every admin access under a grant MUST be recorded in
  an append-only log visible to the affected user.

**Export and deletion (NF-6)**

- **FR-032**: A user MUST be able to export all data they own, and their sharing and access records,
  as JSON and CSV in one archive; later features MUST extend the export to cover their own data.
  The JSON MUST follow a documented format that carries a format version, so a future import feature
  can read it. Importing an export is out of scope for this feature.
- **FR-033**: Export downloads MUST be available only to the requesting user and expire after 7 days.
- **FR-034**: A user MUST be able to permanently delete their account after re-authenticating; deletion
  removes their profile, owned data, tokens and sessions. Deletion MUST be blocked while the user
  owns a household with other members (FR-027) or holds a share in any item co-owned with another
  user; the user MUST be able to give up each such share themselves (to the remaining co-owners or to
  an external owner) without needing the other owners' agreement. A share given to a remaining
  co-owner is pending until accepted (FR-019); deletion need not wait for that acceptance.
- **FR-035**: Deletion MUST also remove the user's data from future backups; existing backups age out
  on their normal retention schedule, and the user is told this before confirming.

### Key Entities *(include if feature involves data)*

- **User**: a person with credentials, language, admin flag and status (active, disabled).
- **Tax profile**: one per user — birth date, region history (region + effective-from date),
  employment type, Social Security summary.
- **Dependant**: belongs to a tax profile — birth year, disability degree, cohabitation.
- **Invitation**: email, inviter, intended household and role (if any), expiry, used/revoked state.
- **Household**: name, owner, shared goals.
- **Household membership**: user, household, role (owner, member, viewer), joined date.
- **Ownership share**: links an item to a user or an external owner, with a percentage and a status
  (pending, accepted); only accepted shares count towards anyone's totals.
- **Sharing setting**: item, household, level (private, visible, editable), included-in-totals flag.
- **Viewer grant**: grantor, viewer, items, optional end date.
- **Support grant**: user, start, end, revoked state.
- **Access log entry**: actor, action, target, time; append-only, visible to the affected user.
- **Personal access token**: owner, name, expiry, last used, revoked state.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An invited person completes sign-up, two-factor setup and tax profile in under 5 minutes.
- **SC-002**: 100% of data-access operations are covered by cross-user denial tests, and all pass.
- **SC-003**: In a test with two households and an admin, zero records cross a household or user
  boundary without an explicit share or grant.
- **SC-004**: A user's export for an account with 50,000 records is ready within 5 minutes, and a
  record-by-record comparison with the live data shows it contains every record the user owns and
  none they do not.
- **SC-005**: After deletion, a search of the live data for the user's identifiers returns nothing.
- **SC-006**: Every admin access under a support grant appears in the user's log within 1 minute.
- **SC-007**: For a 50/50 jointly owned account, each owner's personal total and the household total
  match a hand calculation to the cent.

## Assumptions

- A viewer must have an account on the same instance; nobody outside the instance gets access.
- Detailed contribution history (vida laboral import) is PE-4, phase 3; this feature stores only a
  summary of Social Security history.
- Accounts, assets and transactions are defined in spec 002; this feature defines ownership and
  sharing rules that those items follow.
- Household aggregates of net worth, spending and FIRE are computed by specs 002–004 using the
  inclusion and share rules defined here.
- Email delivery is optional; without it, invitation links are copied by the admin.
- An admin is also an ordinary user with their own financial data; admin privileges never extend to
  other users' data.
- Full audit logging of all events (NF-5) is a later Should item; this feature logs support access
  (FR-031) and admin account actions (FR-029).
- Joint filing (TAX-7) and dependant profiles (USR-7) are out of scope.
- Importing an ascua export (instance migration) is out of scope; a later feature may add it using
  the versioned export format.
