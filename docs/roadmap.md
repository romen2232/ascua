# ascua — path from v1 to a polished product

v1 is scoped in `docs/superpowers/specs/2026-11-16-ascua-v1-design.md` for one small instance
(owner, partner, a few friends, all in Andalusia) plus a public demo. This file records what v1
deliberately leaves out, what a polished, general-audience ascua would need, and why each item waits.
The full wish list is `features.md`; this file is the prioritised gap list.

## 1. Coverage gaps that v1 hard-scopes

| Gap | v1 | Polished | Why it waits |
| --- | --- | --- | --- |
| Regions | Andalusia rule packs only | All 15 common-regime regions; foral packs (Navarra, Basque Country); Canary Islands, Ceuta, Melilla specifics | Every value needs a BOE / regional gazette source and golden tests; no current user needs them |
| Institutions | BBVA, RuralVia, Revolut, CaixaBank, Trade Republic, MyInvestor + generic CSV | Interactive Brokers, DEGIRO, ING, Santander, Openbank, Indexa; migration from Firefly III, Actual, YNAB, Fintonic, spreadsheet template | Only current users' institutions are worth maintaining parsers for |
| Account types | current, savings, broker, cash, property, loan/mortgage | pension plans, term deposits, Letras/bonds, PIAS/unit-linked, EPSV, PPA, gold, private equity, employee equity (RSU, options, ESPP), crypto | Each brings its own tax treatment |
| Couples | Unmarried couple, individual filing | Marital regime (gananciales / separación de bienes), joint filing comparison, separation/divorce/death splits | Not applicable to current users |
| Languages | Spanish, English | Catalan, Galician, Basque | Audience |

## 2. Product depth deferred to later layers

- **Investments and tax**: tax lots, FIFO, traspasos, realised/unrealised gains, two-month rule,
  loss carry-forward and 25% cross-offset, corporate actions, dividends with foreign withholding,
  sale-tax preview, rebalancing, fee analysis.
- **FIRE**: Monte Carlo with documented assumptions, European/global backtesting, after-tax FIRE
  number, Coast and Barista variants, sensitivity analysis, retirement-smile spending, life events,
  saved scenarios side by side.
- **Withdrawal planner**: year-by-year drawdown, tax-aware ordering, bridge to pension, guardrails,
  wealth and solidarity tax, renta vitalicia, filing-threshold awareness.
- **Pensions and Social Security**: plan contributions and limits, withdrawal simulator, vida
  laboral import, public pension estimate, convenio especial, early/partial/delayed retirement.
- **Housing**: rent vs. buy, mortgage amortisation and prepayment, fixed vs. variable, rental
  property, main-home exemptions, plusvalía municipal.
- **Inheritance and gifts (ISD)**, **autónomos** (RETA, Modelo 130/303), **insurance and
  protection**, **region comparison**, **special regimes** (Beckham, exit tax).
- **Spending**: budgets with alerts, subscription price-change alerts, personal inflation vs. IPC.
- **Data quality**: AEAT datos fiscales import and Renta check, broker informe fiscal import,
  data health page, document vault, balance reconciliation, Modelo 720/721 warnings.
- **Alerts and reports**: milestones, year-end reminders, email / ntfy / Gotify / Telegram / push,
  stale-data alerts, monthly review, PDF/CSV adviser reports.

## 3. Platform and security polish

- **Web client quality**: Expo web is accepted for v1 (option A). A polished web experience may need
  a dedicated web client on the same API if Expo web falls short on layout density or WCAG.
- **App-store release** for iOS and Android (v1 uses internal distribution).
- **Auth**: OIDC (Authelia, Authentik, Keycloak), passkeys, scoped read-only API tokens, webhooks.
- **Privacy**: end-to-end encryption, so even server root can't read data (v1 relies on
  "trust the admin's server"); key management and rotation with documented recovery.
- **Mobile**: offline mode, biometric lock, privacy mode that hides amounts, glance view.
- **Bank sync**: PSD2 aggregator, opt-in per user.
- **Ops**: automatic migrations with pre-upgrade backup and rollback, friends self-hosting their
  own instance with easy install and upgrades.

## 4. Open-source and project maturity

- MIT licence, contribution guides, public roadmap, governance for rule-pack review.
- Rule packs installable separately from app upgrades; out-of-cycle releases when a decree changes
  figures; user-set threshold inflation for future years; notice of what changed after a pack update.
- Signed releases, SBOM, reproducible builds, security policy and published threat model.
- Plugin interface for importers and price providers.
- Guided onboarding wizard and an in-app glossary of Spanish tax terms.
