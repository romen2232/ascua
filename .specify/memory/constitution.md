<!--
Sync Impact Report
- Version change: (template) → 1.0.0
- Modified principles: none (initial ratification)
- Added principles:
  I. Privacy-First Self-Hosting
  II. Data-Layer Isolation (NON-NEGOTIABLE)
  III. Rules as Data
  IV. Simulation, Not Advice
  V. Exact Money and Transparent Maths
  VI. Pure, Golden-Tested Tax Engine
  VII. Test-First, Spec-First
- Added sections: Technology and Security Constraints; Development Workflow and Quality Gates;
  Governance
- Removed sections: none
- Templates reviewed: plan-template.md (Constitution Check gate reads this file at runtime),
  spec-template.md, tasks-template.md — no edits required
- Deferred TODOs: none
Remove this comment before committing.
-->

# ascua Constitution

## Core Principles

### I. Privacy-First Self-Hosting

- All user data MUST live on the owner's instance. No data leaves the instance unless a user
  explicitly enables a connector (price provider, bank aggregator), and each connector MUST be
  opt-in and off by default.
- The app MUST ship with no telemetry, analytics, trackers, external fonts or third-party CDN
  assets. Any outbound network call MUST be traceable to a user-enabled connector or an
  admin-configured service (e.g. OIDC, SMTP).
- With every optional service disabled, the app MUST remain fully usable from manual entries and
  CSV imports.
- Instance admins MUST NOT be able to read users' financial data unless that user grants
  time-limited, logged support access.

Rationale: ascua holds several people's complete financial picture; trust depends on it never
phoning home.

### II. Data-Layer Isolation (NON-NEGOTIABLE)

- Every financial record MUST belong to a user or a household, and access MUST be enforced in the
  data layer (scoped querysets/managers as the first layer, PostgreSQL row-level security as the
  second), never only in views or the UI.
- Every API endpoint MUST have an automated test proving that another user, another household's
  member, and an admin without support access cannot read or modify its data.
- Sharing (private / visible / editable) MUST be explicit per item; the default is private.

Rationale: a single leak between users on a shared instance would defeat the product's purpose.

### III. Rules as Data

- No tax rate, bracket, limit, threshold, retirement age or other legal parameter may be
  hardcoded. Each MUST come from a versioned rule pack keyed by tax year and autonomous community.
- Rule packs MUST be plain YAML or JSON files validated against a schema, with a source link (BOE,
  AEAT or Seguridad Social) and an effective date range for every value.
- Projections for years without a published pack MUST use the latest known pack (optionally
  indexed) and MUST say so on screen.

Rationale: Spanish tax rules change yearly and vary by region; updating them must not require a
code change or an app upgrade.

### IV. Simulation, Not Advice

- The app MUST only show the consequences of scenarios the user defines. It MUST NOT recommend
  buying, selling or choosing any specific financial product.
- The core app MUST contain no affiliate links, product rankings or sponsored content.
- Tax figures are estimates: the UI MUST state this and point to the official AEAT Renta WEB
  simulator for filing. The disclaimer MUST appear in the README and on first login.

Rationale: keeps the project neutral, honest about its limits, and clear of CNMV
investment-advice rules.

### V. Exact Money and Transparent Maths

- Monetary amounts MUST be stored and computed as integer cents or `Decimal`, never as floating
  point. Original currency MUST be preserved alongside EUR conversions.
- Dates MUST be ISO 8601. Lots MUST be consumed FIFO; fund transfers (traspasos) MUST preserve
  original cost basis and acquisition dates.
- Every projection and tax figure MUST be expandable to show its inputs, the rule-pack values
  used, the brackets applied, deductions and the result.

Rationale: users act on these numbers; rounding drift or opaque formulas destroy confidence.

### VI. Pure, Golden-Tested Tax Engine

- The tax engine (`backend/taxengine/`) MUST be a pure Python package with no Django imports, no
  I/O beyond reading rule packs, and deterministic outputs.
- Every tax rule MUST have unit tests, and every rule pack MUST ship golden test cases (inputs +
  expected tax). A rule-pack change MUST NOT merge without updated golden tests and source links.

Rationale: the engine is the project's core value; it must be testable and reusable on its own.

### VII. Test-First, Spec-First

- Every feature starts from a spec in `specs/NNN-name/spec.md` that cites requirement IDs from
  `requirements.md` (e.g. USR-1, NF-3). Each requirement ID MUST trace to a spec, a task and a
  test.
- Specs describe behaviour (user stories, Given/When/Then acceptance criteria) and say nothing
  about implementation.
- Within each task, tests MUST be written and seen failing before the implementation.
- When behaviour changes, the spec is updated first and plan/tasks regenerated; drift MUST NOT be
  fixed only in code.

Rationale: traceability is how a small open-source team keeps a tax tool correct over time.

## Technology and Security Constraints

- **Stack**: Django + Django REST Framework, PostgreSQL, Celery + Redis (Celery Beat for
  schedules), OpenAPI 3 via drf-spectacular, React Native (Expo) mobile app for iOS and Android.
  Deviations require a constitution amendment.
- **API**: The mobile app MUST use only the documented REST API. The TypeScript client MUST be
  regenerated from the OpenAPI schema after any serializer change. Personal access tokens support
  scripts and integrations.
- **Deployment**: one `docker compose up` MUST bring up the whole stack and run on a Raspberry Pi 4
  class device.
- **Authentication**: Argon2id password hashing, TOTP two-factor, optional OIDC. Sign-up is
  invitation-based; open registration is off by default.
- **Encryption**: TLS in transit via reverse proxy; database and backups encrypted at rest;
  connector tokens encrypted with a per-instance key.
- **Audit**: logins, sharing changes, admin actions and support access are recorded in an
  append-only log visible to the affected user.
- **GDPR**: each user MUST be able to export all their data (JSON + CSV) and delete their account
  and data.
- **Backups**: scheduled, encrypted, with a documented restore procedure tested in CI.
- **Internationalisation**: Spanish and English at launch; every user-facing string MUST go
  through translation files.
- **Accessibility**: target WCAG 2.2 AA, screen-reader labels and dynamic text sizes.
- **Licence**: MIT. Contributions are accepted under the same licence.

## Development Workflow and Quality Gates

- Work follows Spec Kit: `/speckit-specify` → `/speckit-clarify` → `/speckit-plan` →
  `/speckit-tasks` → `/speckit-analyze` → `/speckit-implement`.
- Every `plan.md` MUST pass a Constitution Check against Principles I–VII before research and again
  after design; any violation is listed in Complexity Tracking with justification or the plan is
  revised.
- A change cannot merge unless: tests, lint and type checks pass for backend and mobile;
  cross-user isolation tests exist for every new or changed endpoint; no hardcoded legal
  parameters were introduced; new user-facing strings are translated; the OpenAPI client is
  regenerated if serializers changed.
- Rule-pack contributions live in `rules/` and follow their own review checklist: an official
  source link for every changed value plus updated golden tests.
- Foral regimes (Navarra, Basque Country) are contributor-maintained packs, not core-team
  commitments.
- Releases use semantic versioning, a changelog and signed container images; an annual release
  follows each year's budget law to update rule packs.

## Governance

- This constitution supersedes other practices and guidance files. `CLAUDE.md` holds day-to-day
  runtime guidance and MUST NOT contradict it.
- Amendments are made via `/speckit-constitution` in a dedicated pull request that states the
  rationale, the version bump and any migration needed for existing specs, plans or code.
- Versioning: MAJOR for removing or redefining a principle; MINOR for adding a principle or section
  or materially expanding guidance; PATCH for clarifications and wording.
- Compliance: every pull request review and every `/speckit-analyze` run checks conformance;
  unjustified violations block merge.

**Version**: 1.0.0 | **Ratified**: 2026-10-29 | **Last Amended**: 2026-10-29
