# ascua v1 — design

Date: 2026-11-16 · Status: awaiting owner approval

## 1. Intent

ascua is a self-hosted, privacy-first personal finance and FIRE app for people living in Spain.

v1 is built for a real, small audience: the owner (Romen), his partner, and a handful of friends,
all on one server run by Romen, plus a public demo page anyone can try without their data being kept.

v1 answers three questions, for each person and for the couple:

1. **Where is my money going?** Real spending, categorised, from real bank data.
2. **How much can I spend?** A monthly "safe to spend" figure after fixed costs and goal saving.
3. **Am I on track for my goals?** For each goal (car, vacation, house, FIRE): how much is needed per
   month, when it will be reached at the current saving pattern, and the gap.

The long feature list in `features.md` (~170 items) is the wish list, and `docs/roadmap.md`
records what v1 leaves out on the way to a polished product. v1 is the smallest slice that
answers the three questions with real data.

## 2. Goals, non-goals, anti-goals

### Goals

- Real data from the six institutions the owner and partner use, with little manual work.
- A couple can share some accounts and goals while keeping others private, with tax-correct
  per-person ownership.
- Friends on the same server are fully isolated from each other and from the admin.
- A public demo that shows the real app with a fictional household and keeps nothing.
- Web, iOS and Android from one client codebase.

### Non-goals (v1; kept on the roadmap)

- Tax lots, FIFO, traspasos, realised gains, sale-tax previews.
- Monte Carlo, tax-aware withdrawal planning, pensions and Social Security estimates.
- Full rent-vs-buy and mortgage tools, ISD, autónomos, insurance, region comparison.
- Joint filing and marital property regime (the couple is unmarried; joint filing is not available
  to them under art. 82 LIRPF). Marriage is a future life event.
- PSD2 bank sync, OIDC, passkeys, notification channels beyond in-app, budgets with alerts.
- Open-source governance, plugin interface, SBOM, separately installable rule packs, Catalan /
  Galician / Basque.
- Friends self-hosting their own instances.

### Anti-goals (would make v1 a failure even if it works)

- **Advice.** ascua never tells a user what product to buy or sell. It shows consequences of
  choices the user defines ("simulation, not advice").
- **Leaking data between users**, or the admin seeing a friend's finances through the app.
- **The demo touching real data**, or keeping what a visitor types.
- **Hard-coded tax values.** Every tax rate, threshold or cost percentage comes from a versioned rule
  pack with a source link.
- **Float money.** Money is integer cents; percentages are integer basis points.

## 3. Users and access

- **Instance admin** (Romen): manages users, invitations and backups. Sees user metadata only, never
  financial data, unless a user grants time-limited, read-only support access, which is logged in a
  log the user can see.
- **Users**: each has their own login and data. Sign-up by invitation only.
- **Household**: two or more users who share some finances (v1: Romen and partner). A user belongs
  to at most one household in v1.
- Authentication: email + password (Argon2id) with mandatory TOTP two-factor. Sessions are revocable.
- Honest trust statement shown to users: the app guarantees the admin cannot see their data through
  ascua; anyone with root on the server can technically read the database. End-to-end encryption is
  out of scope.

Isolation is enforced in the data layer (tenant-scoped managers + PostgreSQL row-level security),
with an automated suite that fails the build if any endpoint or tenant table lacks a cross-user
isolation test. The design in commit `09e147f`, `specs/001-users-households/contracts/isolation.md`
and `data-model.md`, is the starting point and should be recovered from git and trimmed to v1.

## 4. Household and ownership

- Every account and asset has one or more **owners with shares** in basis points, summing to 10000
  (e.g. a joint account at 5000/5000). Default for a new joint account: equal shares.
- Each account has a **visibility** per household: private, visible, or editable.
- **Personal view**: everything the user owns or co-owns, weighted by their share.
  **Household view**: shared items combined into one net worth, spending picture and set of shared
  goals.
- **Shared expenses**: a transaction can be split between household members; ascua shows who owes
  whom and records settlements.
- Permissions (Claude's call): only members of the same household can be co-owners; the admin and
  other users never can. A non-owner household member sees an account only if it is *visible*, and
  can change it only if it is *editable*. Owners always have full access. Splitting a shared expense
  is independent of ownership shares (a 50/50 account can pay a 70/30 expense).
- Leaving a household (Claude's call): per-person goal contributions and ownership shares stay on
  record; shared items need an explicit ownership resolution before the member leaves.
- Per-person tax figures use ownership shares (relevant later when tax lots arrive; in v1 it drives
  per-person net worth and wealth figures).

## 5. Accounts, import and net worth

- Account types in v1: current, savings, broker (funds / ETFs / stocks), cash, property, loan /
  mortgage. Other types stay on the roadmap.
- **Manual entry** of balances, transactions and holdings.
- **Importers** for exactly six institutions: BBVA, RuralVia (Caja Rural), Revolut, CaixaBank,
  Trade Republic, MyInvestor. Banks give transactions and balances; brokers give cash movements and
  holdings. A generic **CSV importer with saved column mappings** covers anything else.
- Before building each importer, verify which export formats the institution offers today (CSV,
  XLSX, PDF statement). If one only offers PDF, the builder decides between a PDF parser and the
  generic CSV path, and records why.
- **Import preview with undo**: an import is shown before it is committed and can be rolled back as a
  unit. **Duplicate detection** across repeated imports.
- **Transfer matching**: moves between a user's own accounts (or a household member's) are not
  spending or income.
- **Holdings** are quantity × price. No lots in v1. Prices: CNMV daily NAV by ISIN for funds; one
  additional provider for ETFs and stocks (builder's choice, must be free, opt-in by the admin, and
  replaceable). Non-EUR holdings are converted with ECB reference rates.
- **Net worth over time**, split by asset class, liquidity and owner.

## 6. Spending and "safe to spend"

- Categories with **rules** (e.g. merchant contains "Mercadona" → Groceries). Rules apply on import;
  manual recategorisation can create a rule.
- Each category is tagged **essential** or **discretionary**.
- **Savings rate** per month and rolling 12 months, per user and per household.
- **Recurring and irregular costs**: recurring charges are detected; irregular known costs (IBI, car
  insurance, …) are set up as **sinking funds** that spread the cost evenly over the months before it
  is due.
- **Safe to spend (this month)** = expected income − recurring costs − sinking-fund contributions −
  planned goal saving − non-recurring spending so far this month. Each term is expandable to show
  where it came from.
  - *Expected income* (Claude's call): detected recurring income (e.g. salary) for the month,
    editable by the user; if none is detected, the trailing 3-month average income.
  - *Planned goal saving* (Claude's call): a fixed euro amount computed once at the start of each
    month = Σ goal percentages × the user's 12-month average actual savings. It is a target, not a
    record: what goals actually receive is still the percentage of the month's *actual* savings
    (section 7), computed at month close. This avoids the circularity of budgeting against a number
    that depends on the spending being budgeted.
  - *Unassigned savings percentage* (owner's decision): treated as a **buffer**. Its share of the
    12-month average savings is subtracted like goal saving and is never shown as spendable. The
    buffer's accumulated total is shown on its own.

## 7. Goals

Goal kinds in v1: **simple** (car, vacation, anything with an amount and a date), **house**, and
**FIRE**.

### Common behaviour

- A goal has a name, target amount, target date (optional for FIRE), owner (one user, or shared by
  household members), and status (active, reached, spent, archived).
- **Funding by percentage.** Each user assigns a percentage of their own **actual monthly savings**
  (real income − real spending for that month) to each goal they take part in. A user's
  percentages across all their goals (solo and shared) total at most 100%; the rest is unassigned.
- For a shared goal, each member sets their own percentage; the goal receives the sum. Contributions
  are tracked **per person**, and ascua shows the split (e.g. 60/40 of a house deposit).
- **Months with negative savings** assign nothing; money already earmarked is never taken back
  automatically, and the month is flagged.
- **When a goal is reached**, its percentage is redistributed to that user's remaining goals in
  proportion to their current percentages, and the user is told. Users can change percentages at any
  time.
- **Earmarks, not accounts.** Money for a goal is a running total, not a bank account. ascua checks
  that the sum of earmarks never exceeds what the user actually holds, and flags it if it does.
  "Holds" (Claude's call) = the user's share of liquid assets: current, savings and cash accounts,
  plus broker holdings at market value. Property and loans are excluded.
- For each goal ascua shows: **target**, **needed per month** to hit the date, **projected date** at
  the current pattern (12-month average savings × percentage, plus expected return if the user sets
  one), and **gap** in €/month and in months.
- **What-if**: changing a percentage shows the effect on every goal's projected date live, before
  saving the change.
- When the goal is used (car bought), the user marks it spent and links the purchase transaction.

### House goal

- Target = deposit + purchase costs, not the full price. Inputs: expected price, region, new or
  second-hand, deposit percentage (default 20%).
- Purchase costs: ITP (second-hand) or VAT + AJD (new), notary, registry, gestoría, agency, valuation.
  Tax rates come from a regional rule pack; fees use documented estimate ranges, also as data.
- Region coverage (owner's decision): **Andalusia only** in v1, since every current user lives there.
  The pack includes Andalusia's reduced rates where they apply. A house goal in another region
  shows an "unsupported region" message rather than a guess. More regions: see `docs/roadmap.md`.
- The breakdown is expandable. Mortgage and rent-vs-buy maths are out of v1.

### FIRE goal

- FIRE number = annual spending ÷ withdrawal rate (default 3.5%, editable). Annual spending defaults
  to the last 12 months of actual spending, editable. Lean (essential-only) and Fat variants are shown
  alongside.
- Deterministic projection with editable real return and inflation (default from INE IPC history,
  stored in a rule/data pack with source). Shows needed monthly saving and projected FIRE date / age.
- Every number is expandable to its formula and inputs. Figures are labelled gross of tax.

### Wording (Claude's call)

"Needed per month" and projected dates are arithmetic facts about the user's own targets, not
advice, and may be shown. Copy never names a product, provider or asset to buy or sell, and never
says "you should". A "simulation, not advice" notice is acknowledged at first sign-in and linked
from every projection screen.

## 8. Demo

- A **separate deployment** of the same code with `DEMO_MODE` on, its own database and secrets.
  It never runs on the real instance.
- Each visitor gets a **throwaway sandbox**: a fresh copy of a fictional household (two people,
  accounts at the six institutions, a year of transactions, all four goal kinds). Visitors can edit
  everything.
- Sandboxes are deleted after a period of inactivity (default 2 hours) and on a hard cap (default
  24 hours). A visible banner says data is not kept.
- Disabled in demo: price fetching (frozen prices), email, invitations, real uploads beyond the
  sample files, support access, exports. Rate limited per IP.
- The fictional household is also the main test fixture and screenshot source.
- Hosting (Claude's call): its own compose project with its own database container. A separate host
  is preferred; if it shares the owner's server, it gets resource limits so visitors can't starve the
  real instance.

## 9. Platform and stack (chosen: option A)

**Approaches considered**

- **A. Django + DRF backend, one Expo app for web, iOS and Android.** Chosen. Reuses the earlier
  research and spec 001 work; one UI codebase; native app on phones. Trade-off: web from Expo is less
  polished, and three targets are tested from day one.
- B. Django + DRF backend, React web app only (PWA). Fastest to real data, least client work; no
  native app. Recommended by Claude, not chosen.
- C. Full-stack TypeScript (Next.js). Rejected: decimal money maths and a pure rule engine fit Python
  better, and it discards prior research.

**Stack** (carried over from the previous plan, trimmed to v1): Python 3.13, Django 5.2 LTS, DRF,
drf-spectacular, SimpleJWT, django-otp, argon2-cffi, django-axes, Celery + Redis, PostgreSQL 17 with
row-level security. Client: Expo (web + iOS + Android), TypeScript strict, expo-router, TanStack
Query, openapi-fetch with a generated client, i18next (Spanish and English).

**Reuse of earlier work** (Claude's call): this document wins on names and scope. The isolation
pattern from commit `09e147f` (TenantManager, RLS migrations, `ScopedViewSet`, route registry and
coverage test) is mandatory, not optional; its user, household and sharing models are trimmed to
this document. Old `taxengine/` is replaced by the per-context `domain/` layers; `mobile/` becomes `app/`.

**Native distribution** (Claude's call): v1 iOS/Android builds go to the owner's, partner's and
friends' phones through Expo internal distribution (EAS or local builds); no app-store release in
v1. Web is the demo target and must meet WCAG 2.2 AA.

**Backend architecture (owner's decision): DDD with Screaming Architecture, pure domain in every
context.**

Top level of `backend/` names bounded contexts, not frameworks:

```text
backend/
├── shared_kernel/     # Money (int cents), BasisPoints, Actor, DomainEvent, clock, ids
├── identity/          # users, invitations, TOTP, sessions, support access
├── households/        # household, membership, ownership shares, visibility
├── ledger/            # accounts, transactions, holdings, transfers, net worth
├── importing/         # per-institution parsers, CSV mappings, preview/undo, duplicates
├── spending/          # categories, rules, recurring, sinking funds, savings rate, safe to spend
├── goals/             # goals, percentages, earmarks, contributions, projections, what-if
├── planning/          # FIRE number and deterministic projection
├── market_data/       # price providers (CNMV, ETF/stock), ECB FX
├── rules/             # rule-pack loading and validation (packs themselves live in /rules)
├── demo/              # sandbox lifecycle, fictional household seeding
└── config/            # Django settings, root urls, Celery app (the only framework-named folder)
```

Every context has the same four layers:

- `domain/` — entities, value objects, aggregates, domain services, repository interfaces
  (ports). Plain Python, deterministic. **No Django, DRF or Celery imports.**
- `application/` — use cases (commands and queries) orchestrating the domain through ports.
  No Django imports.
- `infrastructure/` — Django ORM models, repository implementations that map ORM ↔ domain,
  migrations (including RLS), external adapters (price providers, file parsers I/O), Celery tasks.
- `api/` — DRF serializers, views and routes; thin, calling application use cases.

Rules:

- The layer direction (`api` → `application` → `domain`; `infrastructure` implements `domain`
  ports) and "no framework imports in `domain`/`application`" are enforced in CI with
  import-linter. Contexts talk to each other only through their `application` layer or domain
  events, never by importing another context's models.
- Tenant isolation sits in infrastructure: repositories take an `Actor` and query only through
  `TenantManager`; RLS stays underneath as the second wall. The isolation registry covers every
  route; the coverage test covers every ORM model.
- Domain tests run without a database; repository and API tests run against PostgreSQL.
- Accepted cost: each aggregate has a domain class, an ORM model and a mapper, including simple
  ones (e.g. invitations).

**Other folders**: `rules/ES/<year>/AN/` (YAML packs with a source link per value and golden tests),
`app/` (Expo client).

**Deployment**: `docker compose up` on a single small server (Raspberry Pi 4 class, arm64 and
amd64). Scheduled encrypted backups with a documented, tested restore.

## 10. Constraints

- Privacy: no telemetry, trackers, external fonts or CDNs. Outbound calls only to price/FX providers
  and SMTP, both enabled by the admin.
- Rules as data: no hard-coded tax value; every value has a BOE / AEAT / regional source link and
  golden tests.
- Exact money: integer cents, basis points, ISO 8601 dates.
- Transparent maths: every figure expands to its inputs and formula.
- Spanish and English for all user-facing strings.
- Accessibility: WCAG 2.2 AA on the web target.
- Test-first: every task writes its tests first and sees them fail.

## 11. Delivery order

Each slice ends with something usable by the owner.

1. **Foundation**: repo, compose, auth with TOTP, invitations, isolation layer and suite, client
   scaffold for all three targets, generated API client, i18n.
2. **Accounts + manual entry + net worth**, household and ownership shares, visibility.
3. **Importers + import preview/undo + duplicates + transfer matching**, one institution at a time,
   starting with the owner's main bank.
4. **Spending**: categories, rules, essential/discretionary, savings rate, recurring detection,
   sinking funds, shared-expense settlement.
5. **Goals**: simple goals, percentages, projections, what-if; then house; then FIRE.
6. **Safe to spend.**
7. **Prices and holdings** (CNMV, ETF/stock provider, ECB FX).
8. **Demo deployment** with the fictional household and sandbox lifecycle.
9. **Ops polish**: backups/restore, support access, GDPR export and deletion.

## 12. Left to the builder

- Per-institution parsing details and file formats (after verifying current exports).
- Choice of the ETF/stock price provider, within the constraints above.
- Recurring-charge detection heuristics.
- Exact sandbox implementation (schema-per-sandbox, tenant rows, or database clone), as long as
  sandboxes are isolated from each other and deleted on schedule.
- Screen layouts, within WCAG 2.2 AA and Spanish/English.
- How spec-per-feature documents are organised for implementation.
