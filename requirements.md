# ascua — Requirements

Oct 29, 2026 · @Romen Medina

## Overview

ascua (Spanish for a glowing ember) is an open-source, self-hosted app that tells each user how far they are from financial independence in Spain, and how to get there and withdraw with the least tax. It replaces US-centric FIRE tools with a Spanish tax, pension and Social Security engine.

**In scope:** net worth and expense tracking, FIRE projections, Spanish tax modelling (IRPF savings base, fund transfers, pension plans, regional wealth taxes), public pension estimates, withdrawal planning, multiple users and households on one instance, used through a React Native app for iOS and Android.

**Out of scope (v1):** executing trades or payments, tax filing, and personalised investment recommendations.

**Principles**

- **Self-hosted and privacy-first.** Data lives on the owner's server; no telemetry by default; nothing leaves the instance unless a user enables a connector.
- **Multi-user from day one.** Every record belongs to a user or a household; isolation is enforced in the data layer, not only in the UI.
- **Rules as data.** Tax rates, limits and regional rules are versioned configuration by year and region, editable without code changes.
- **Simulation, not advice.** The app shows the consequences of scenarios the user defines. It never tells a user what to buy or sell.
- **Transparent maths.** Every projection and tax figure can be expanded to show its inputs and formula.

## Users, roles and households

Each person has their own account and tax profile, and can join a household to share selected accounts and plan FIRE together. Spanish tax is mostly individual, so the household is a planning layer on top of individual tax calculations, with optional joint filing (tributación conjunta) as a scenario.

| Role | Scope | Can do |
| --- | --- | --- |
| Instance admin | Whole server | Manage users, invitations, backups, tax-rule packs, connectors; no access to users' financial data by default |
| Household owner | One household | Invite or remove members, set shared goals, choose which shared accounts count towards the household FIRE number |
| Member | Own data + shared items | Full control of own accounts; read or edit shared accounts per permission |
| Viewer | Granted items | Read-only, e.g. a partner or a trusted adviser |

**Requirements**

- **USR-1 (Must)** Each user has an individual profile: birth date, autonomous community of tax residence, employment type (employee, autónomo, none), dependants, Social Security history.
- **USR-2 (Must)** Accounts and assets have an owner and an ownership share, so a jointly held account (e.g. 50/50) is split correctly for each person's tax.
- **USR-3 (Must)** Households aggregate members' shared items into combined net worth, spending and FIRE projections.
- **USR-4 (Should)** Item-level sharing: a member chooses per account whether it is private, visible or editable by the household.
- **USR-5 (Must)** Admins cannot read financial data unless a user grants support access, which is time-limited and logged.
- **USR-6 (Should)** Invitation-based sign-up; open registration disabled by default.
- **USR-7 (Could)** Child or dependant profiles for modelling education costs and inheritance.

## Functional requirements

Thirty-nine requirements across eight modules; the 19 marked Must make up the MVP. Priorities use MoSCoW (Must, Should, Could).

### Accounts and net worth

| ID | Requirement | Priority |
| --- | --- | --- |
| NW-1 | Account types: current, savings, investment fund, ETF/stock broker, pension plan (individual, employment, PPA), property, mortgage, loan, crypto, cash | Must |
| NW-2 | Manual balances and transactions, plus CSV import with saved column mappings; launch importers for Santander, BBVA, Caja Rural, Revolut, Trade Republic and MyInvestor | Must |
| NW-3 | Net worth over time, split by asset class, liquidity (available now vs. locked until a date) and owner | Must |
| NW-4 | Daily price updates from pluggable providers; the first ingests CNMV public fund publications (daily CSV/XML files and regulatory disclosures) by ISIN | Should |
| NW-5 | Bank sync through PSD2 open banking aggregators, optional and per user | Could |
| NW-6 | Multi-currency holdings converted to EUR, keeping original currency for tax | Should |

### Spending and savings

| ID | Requirement | Priority |
| --- | --- | --- |
| SP-1 | Categorised transactions with rules (e.g. merchant contains "Mercadona" → Groceries) | Must |
| SP-2 | Each category tagged essential or discretionary, to drive Lean and Fat FIRE numbers | Must |
| SP-3 | Savings rate per month and rolling 12 months, per user and per household | Must |
| SP-4 | Annual spending forecast that separates one-offs (car, IBI, insurance) from recurring costs | Should |
| SP-5 | Budgets per category with alerts | Could |

### FIRE engine

| ID | Requirement | Priority |
| --- | --- | --- |
| FI-1 | FIRE number from annual spending and an adjustable withdrawal rate (default 3.5%), shown gross of tax | Must |
| FI-2 | Variants: Lean, Regular, Fat, Coast and Barista FIRE | Must |
| FI-3 | Deterministic projection with user-set real return, inflation (default from INE IPC history) and contributions | Must |
| FI-4 | Monte Carlo simulation (≥ 1,000 runs) using historical or parametric returns, reporting probability of success | Should |
| FI-5 | Saved scenarios compared side by side (e.g. +€300/month, move region, part-time from 45) | Should |
| FI-6 | Life events on the timeline: house purchase, children, inheritance, job change, sabbatical | Should |

### Investments and tax lots

| ID | Requirement | Priority |
| --- | --- | --- |
| IN-1 | Every purchase stored as a lot; sales consume lots FIFO, as Spanish law requires | Must |
| IN-2 | Fund transfers (traspasos) carry the original cost basis and dates without triggering tax | Must |
| IN-3 | Realised and unrealised gains per year and per lot | Must |
| IN-4 | Two-month rule: flag losses that cannot be offset because the same asset was bought within two months (one year for unlisted) | Should |
| IN-5 | Dividends and interest recorded with withholding at source, including foreign withholding for double-taxation relief | Should |

### Pension plans and Social Security

| ID | Requirement | Priority |
| --- | --- | --- |
| PE-1 | Pension plan contributions with annual limits and the resulting IRPF deduction | Must |
| PE-2 | Withdrawal simulator: lump sum vs. annual income vs. mixed, with tax as work income and the 40% reduction for pre-2007 contributions | Must |
| PE-3 | Liquidity dates: contributions older than ten years treated as withdrawable | Should |
| PE-4 | Public pension estimate from contribution history (vida laboral import) and contribution bases | Must |
| PE-5 | Early-exit impact: pension at legal age if the user stops working at age X | Must |
| PE-6 | Convenio especial: cost of voluntary contributions after leaving work vs. pension gained | Should |

### Withdrawal planner

| ID | Requirement | Priority |
| --- | --- | --- |
| WD-1 | Year-by-year drawdown from FIRE date to age 95: which assets to sell, gross amount, tax, net income | Must |
| WD-2 | Tax-aware ordering: fill low savings-base brackets with gains, time pension plan withdrawals, use cash buffer | Should |
| WD-3 | Bridge view: portfolio needed until pension age and after pension starts | Must |
| WD-4 | Guardrails: spending cuts after bad years, configurable | Could |

### Housing and property

| ID | Requirement | Priority |
| --- | --- | --- |
| HO-1 | Rent vs. buy with purchase costs (ITP or VAT, notary, registry, agency) and IBI | Should |
| HO-2 | Mortgage amortisation, and prepayment vs. investing comparison | Should |
| HO-3 | Rental property: net yield after expenses and rental income tax rules | Could |

### Alerts and reporting

| ID | Requirement | Priority |
| --- | --- | --- |
| AL-1 | Milestones: 10/25/50/75/100% of FIRE number, Coast FIRE reached, one year of expenses saved | Must |
| AL-2 | Year-end reminders: pension contribution before 31 December, loss harvesting window | Should |
| AL-3 | Modelo 720/721 threshold warnings for foreign assets and foreign-held crypto | Should |
| AL-4 | Annual tax summary per user to help prepare the Renta return (gains, dividends, deductions) | Should |

## Spanish tax and rules engine

All tax figures come from versioned rule packs keyed by tax year and autonomous community, never from code. Spain has changed savings-base brackets and wealth-tax rules several times since 2021, and each region sets its own general-base scale and wealth-tax reliefs.

**Rule pack contents**

| Rule | Varies by | Used by |
| --- | --- | --- |
| Savings base (base del ahorro) brackets and rates | Year | IN-3, WD-1, AL-4 |
| General base scale: state half + regional half | Year, region | PE-2, WD-1 |
| Personal and family minimums | Year, region | All IRPF calculations |
| Pension plan contribution limits and deduction caps | Year | PE-1 |
| Pre-2007 pension contribution reduction and lump-sum windows | Year | PE-2 |
| Patrimonio: exemption, scale, regional relief | Year, region | WD-1, alerts |
| Solidarity tax on large fortunes | Year | WD-1, alerts |
| Modelo 720/721 thresholds | Year | AL-3 |
| Social Security: legal retirement age, required years, contribution bases, pension calculation period | Year | PE-4, PE-5, PE-6 |
| Rental income reductions | Year, contract date | HO-3 |

**Requirements**

- **TAX-1 (Must)** Rule packs are plain files (YAML or JSON) with a schema, a source link per value and an effective date range.
- **TAX-2 (Must)** Projections for future years use the latest known pack, optionally indexed, and say so on screen.
- **TAX-3 (Must)** Every calculated tax figure shows a breakdown: base, brackets applied, deductions, result.
- **TAX-4 (Should)** Golden test cases per pack (inputs + expected tax), so contributors can update rules safely.
- **TAX-5 (Should)** Packs are shipped with releases and also installable separately, so a rule change does not need an app upgrade.
- **TAX-6 (Could)** Foral regimes (Navarra, Basque Country) as separate packs maintained by contributors, not by the core team.

* **TAX-7 (Should, phase 2)** Joint filing (tributación conjunta) for a household, compared side by side with individual filing.

The engine is an estimate. The UI states this and points users to the official Renta WEB simulator for filing.

## Non-functional requirements

The app must be easy to run on a home server or a cheap VPS, and safe enough to hold several people's complete financial picture.

| ID | Area | Requirement | Priority |
| --- | --- | --- | --- |
| NF-1 | Deployment | One `docker compose up` brings up Django, PostgreSQL, Redis and the Celery worker; runs on a Raspberry Pi 4 class device | Must |
| NF-2 | Authentication | Password with Argon2id hashing, TOTP two-factor, optional OIDC (Authelia, Authentik, Keycloak) | Must |
| NF-3 | Isolation | Every query scoped by user or household in the data layer (e.g. PostgreSQL row-level security); automated tests prove cross-user access fails | Must |
| NF-4 | Encryption | TLS in transit via reverse proxy; database and backups encrypted at rest; connector tokens encrypted with a per-instance key | Must |
| NF-5 | Audit | Log of logins, sharing changes, admin actions and support access, visible to the affected user | Should |
| NF-6 | GDPR | Each user can export all their data (JSON + CSV) and delete their account and data | Must |
| NF-7 | Backups | Scheduled encrypted backups with documented restore, tested in CI | Must |
| NF-8 | Privacy | No telemetry, external fonts or trackers by default; price and bank connectors opt-in | Must |
| NF-9 | Performance | Dashboard loads in < 1 s with 10 years of data and 50,000 transactions; Monte Carlo of 1,000 runs in < 3 s | Should |
| NF-10 | Accuracy | Money stored as integer cents or decimal, never floats; unit tests for every tax rule | Must |
| NF-11 | Languages | Spanish and English at launch; translation files open to contributors | Must |
| NF-12 | Accessibility | WCAG 2.2 AA; React Native app for iOS and Android with screen-reader labels and dynamic text sizes | Should |
| NF-13 | API | DRF REST API documented with OpenAPI; the mobile app uses it, and personal access tokens allow scripts and integrations | Must |

## Architecture and data model

A Django REST Framework backend plus PostgreSQL keeps self-hosting simple, with a React Native app as the client; the tax engine is a pure library that reads rule packs, so it can be tested and reused on its own.

&#91;embedded content: system architecture · one app container, database, rule files, optional services\]

Everything external is optional and off by default; with all of it disabled the app still works from manual entries and CSV imports.

**Core entities**

| Entity | Key fields | Notes |
| --- | --- | --- |
| User | birth date, region, employment type, locale | Tax profile per person |
| Household | name, owner | Planning layer; members via HouseholdMember (role) |
| Account | type, institution, currency, liquidity date | Owners via AccountOwner (user, share %) |
| Instrument | ISIN, ticker, type (fund, ETF, stock, crypto) | Prices in a separate time series |
| Transaction | date, amount, category, account | Money in integer cents |
| Lot | instrument, quantity, cost, acquisition date | Consumed FIFO on sale |
| Transfer (traspaso) | from fund, to fund, lots moved | Keeps original cost and dates |
| PensionContribution | plan, date, amount, employer or personal | Pre-2007 flag for the reduction |
| ContributionHistory | period, base, regime | From vida laboral import |
| Scenario | assumptions, life events, withdrawal rate | Owned by user or household |
| AuditEvent | actor, action, target, time | Append-only |

**Chosen stack**

| Layer | Choice | Notes |
| --- | --- | --- |
| Backend | Django + Django REST Framework | Python suits the financial maths; NumPy for Monte Carlo |
| Database | PostgreSQL | Row-level security as a second isolation layer behind queryset scoping |
| Background jobs | Celery + Redis, Celery Beat for schedules | CNMV price ingestion, imports, alerts, backups |
| API contract | OpenAPI 3 via drf-spectacular | Generates a typed TypeScript client for the app |
| Auth | dj-rest-auth + SimpleJWT, django-otp for TOTP | Token auth suited to a mobile client |
| Mobile app | React Native (Expo suggested) | iOS and Android; a web client can follow with React Native Web |
| Tax engine | Pure Python package in the repo, no Django imports | Tested alone against golden cases |

## Open-source governance

Licensed under MIT: anyone can use, modify and redistribute the code, including in closed products, as long as they keep the copyright notice.

- **Repository:** public on GitHub or Codeberg, with README, CONTRIBUTING, CODE\_OF\_CONDUCT and SECURITY (private vulnerability reporting).
- **Rule-pack contributions:** a separate folder with its own review checklist; every changed value needs a link to BOE, AEAT or Seguridad Social, plus updated golden tests.
- **Releases:** semantic versioning, changelog, signed container images; an annual release after each year's budget law updates the rule packs.
- **Disclaimer:** shown in the README and on first login. The software is an educational simulation, not financial, tax or legal advice, and makes no recommendation to buy or sell any product. Keeping it this way also keeps the project clear of CNMV investment-advice rules.
- **No affiliate links or product rankings** in the core app, so the project stays neutral.
- **Sample data:** a fictional demo household for screenshots, tests and try-before-you-install.

## Roadmap and decisions

Build the MVP for your own household first, then the Spanish tax core; open the project publicly only once the tax figures match a real Renta return.

&#91;embedded content: roadmap · 4 phases, 3 gates\]

Phase 1 covers the Must items in NW, SP, FI, USR and NF; phase 2 adds IN, PE-1 to PE-3 and TAX, including joint filing; phase 3 adds PE-4 to PE-6, WD and FI-4 to FI-6; phase 4 holds the remaining Should and Could items.

**Decisions**

| Topic | Decision |
| --- | --- |
| Stack | Django REST Framework + PostgreSQL backend; React Native app |
| License | MIT |
| First importers | Santander, BBVA, Caja Rural, Revolut, Trade Republic, MyInvestor |
| Fund prices | CNMV public daily publications and disclosures |
| Joint filing | Phase 2 (TAX-7) |
| Foral regimes | Left to contributors |

**Still open**

- [ ] Price source for ETFs and stocks, e.g. Trade Republic holdings not covered by CNMV fund data
- [ ] Confirm CNMV file formats, update times and reuse terms before building the ingester

## Spec-driven development with Claude

Build every feature through GitHub Spec Kit with Claude Code: this document seeds the project constitution, and each requirement ID traces to a spec, a task and a test.

**Workflow**

1. Initialise the repo with `specify init ascua --integration claude`, which installs the Spec Kit commands for Claude Code. Flags change between versions, so check `specify --help` first.
2. Run `/speckit.constitution` once with the non-negotiables: privacy-first, rules as data, simulation not advice, money in integer cents, tax engine as pure Python with golden tests, cross-user isolation tests on every endpoint, MIT licence.
3. For each feature run `/speckit.specify` with its requirement IDs. The resulting `spec.md` holds user stories and Given/When/Then acceptance criteria, and says nothing about implementation.
4. Run `/speckit.clarify` to surface gaps, then `/speckit.plan` for `plan.md`: DRF models, serializers, endpoints, Celery tasks and React Native screens.
5. Run `/speckit.tasks` for `tasks.md`, review it, then `/speckit.implement`. Tests come before code in each task.
6. When behaviour changes, update the spec first and regenerate plan and tasks; never fix drift only in code.

**Repository layout**

```
ascua/
├── CLAUDE.md
├── .specify/memory/constitution.md
├── specs/
│   ├── 001-users-households/
│   │   ├── spec.md
│   │   ├── plan.md
│   │   └── tasks.md
│   └── 002-accounts-import/
├── backend/          # Django + DRF
│   └── taxengine/    # pure Python, no Django
├── rules/ES/2026/    # YAML rule packs
└── mobile/           # React Native
```

**CLAUDE.md should state**

- Commands to run tests, lint and type checks for backend and mobile.
- Never hardcode a tax rate, limit or threshold; read it from a rule pack.
- Every queryset is scoped by user or household; add an isolation test for each new endpoint.
- Money is integer cents; dates are ISO; all user-facing strings go through translation files.
- Regenerate the TypeScript API client after any serializer change.

**Phase 1 specs**

| Spec | Requirements |
| --- | --- |
| 001-users-households | USR-1 to USR-6, NF-2, NF-3, NF-6 |
| 002-accounts-import | NW-1 to NW-3; one importer task per bank or broker |
| 003-spending | SP-1 to SP-3 |
| 004-fire-engine | FI-1 to FI-3, AL-1 |
| 005-ops | NF-1, NF-7, NF-8, NF-10, NF-11 |

Sources: [GitHub Spec Kit](https://github.com/github/spec-kit) · [Spec Kit with Claude Code from the command line](https://www.testmuai.com/blog/spec-driven-development-command-line/)