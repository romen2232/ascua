# features

ascua: complete feature list
Nov 16, 2026 · @Romen Medina
The original list is strong on accounts, FIRE maths and tax lots; the biggest gaps are inheritance and gift tax, self-employed workers, loss carry-forward, employee equity, and getting data in from AEAT and other tools. Items marked New below are suggested additions; everything else is from the original list.
The ten most meaningful gaps
1.  Inheritance and gift tax (ISD) by region. The app models inheritance as a life event but not the tax on it, which varies hugely between regions.
2.  Loss carry-forward and cross-offset. Savings-base losses carry forward four years and can offset up to 25% of the other savings-base block. Without this, the gains figures are wrong for anyone with past losses.
3.  Autónomos support. "Employment type" exists, but there is no RETA quota by real income, quarterly Modelo 130/303 or deductible expenses. Many FIRE-minded people are self-employed.
4.  AEAT datos fiscales import. Importing the tax agency's own data file is the cheapest way to check the app's figures each year.
5.  Employee equity. RSUs, stock options and ESPPs, with the employment-income tax at vest and a separate cost basis.
6.  Post-FIRE costs. Private health insurance, voluntary Social Security contributions and long-term care are what Spanish early retirees most often under-budget.
7.  Region comparison. Moving region changes the general-base scale, wealth tax and ISD; a side-by-side view supports a real decision.
8.  Price and FX sources beyond CNMV. ETFs, stocks, crypto and ECB exchange rates need providers too, or net worth goes stale.
9.  Corporate actions. Splits, mergers, spin-offs and ticker changes break FIFO lots if they are not handled.
10.  Migration importers. Importers from spreadsheets, Firefly III, Actual and Fintonic lower the cost of switching.
Users and households
• Individual tax profile: birth date, region, employment type, dependants, Social Security history
• Shared ownership of accounts (e.g. 50/50), with tax split per person
• Households that combine net worth, spending and FIRE projections
• Per-account sharing: private, visible or editable
• Roles: instance admin, household owner, member and viewer
• Admins can't read financial data unless a user grants time-limited, logged support access
• Invite-only sign-up
• Child and dependant profiles (education costs, inheritance)
• Marital property regime per couple (gananciales, separación de bienes), which sets default ownership of new assets
• Emergency access: a trusted person gets read access after a waiting period if the owner doesn't respond
• Household changes over time: separation, divorce or death splits accounts and history cleanly
• Planned change of tax residence (another region or abroad) on a user's timeline
Accounts and net worth
• Account types: current, savings, funds, ETF/stock broker, pension plans, property, mortgage, loan, crypto and cash
• Manual entry and CSV import with saved mappings
• Launch importers for Santander, BBVA, Caja Rural, Revolut, Trade Republic and MyInvestor
• Net worth over time, split by asset class, liquidity and owner
• Daily fund prices from CNMV by ISIN, through pluggable price providers
• Optional PSD2 bank sync
• Multi-currency holdings converted to EUR, with the original currency kept for tax
• More account types: term deposits, Letras del Tesoro and bonds, PIAS and unit-linked insurance, EPSV, employer pension plans, PPA, physical gold, private and startup equity
• Employee equity: RSUs, stock options and ESPP with vesting schedules
• Price providers for ETFs, stocks and crypto, plus ECB reference FX rates
• Property valuation: purchase price, cadastral value and an optional indexed estimate
• Year-end and Q4 average balances stored per account (needed for Modelo 720 and wealth tax)
• Importers for Interactive Brokers, DEGIRO, ING, CaixaBank, Indexa Capital and Openbank
• Balance reconciliation: computed vs. reported balance, with a flag on mismatch
Spending and savings
• Categorised transactions with auto-categorisation rules
• Essential vs. discretionary tags, which drive the Lean and Fat FIRE numbers
• Savings rate per month and rolling 12 months, per user and per household
• Annual spending forecast that separates one-offs from recurring costs
• Category budgets with alerts
• Transfer matching between own accounts, so moves aren't counted as spending or income
• Split transactions and shared-expense settlement between household members
• Subscription and recurring-charge detection, with price-change alerts
• Duplicate detection across imports and PSD2 sync
• Personal inflation rate from the user's own spending basket, compared with INE IPC
• Sinking funds for irregular costs (car, holidays, IBI)
FIRE engine
• FIRE number from annual spending and a withdrawal rate (default 3.5%)
• Lean, Regular, Fat, Coast and Barista FIRE variants
• Deterministic projection with real return, inflation (INE IPC) and contributions
• Monte Carlo simulation (1,000+ runs) with a probability of success
• Saved scenarios compared side by side
• Life events on the timeline: house, children, inheritance, job change, sabbatical
• After-tax FIRE number, using the rules engine instead of a gross withdrawal rate
• Historical backtesting on European and global data, not only US series, with a documented data source
• Post-FIRE cost items: private health insurance, convenio especial, long-term care
• Sensitivity analysis: which inputs (return, inflation, spending, pension) move the FIRE date most
• Spending that changes with age (the "retirement smile") instead of flat real spending
• Monte Carlo settings shown openly: return model, correlations, seed, fat tails
Investments and tax lots
• Every purchase stored as a lot, with FIFO sales
• Fund transfers (traspasos) that keep the original cost basis and dates
• Realised and unrealised gains per year and per lot
• Two-month rule detection for losses that can't be offset
• Dividends and interest with withholding, including foreign withholding for double-taxation relief
• Loss carry-forward for four years, plus the 25% cross-offset between gains and returns in the savings base
• Corporate actions: splits, reverse splits, mergers, spin-offs, ISIN changes and scrip dividends
• Asset allocation targets with tax-aware rebalancing suggestions (new money first, traspasos next, sales last)
• Fee analysis: TER, custody and FX fees, and their cost over the plan
• Crypto lots with swaps between coins treated as taxable disposals
• Sale preview: tax due on selling a given amount before the user sells it
• Fund and ETF look-through by region and sector
Pension plans and Social Security
• Plan contributions with annual limits and the IRPF deduction
• Withdrawal simulator: lump sum, annual income or mixed, including the 40% pre-2007 reduction
• Liquidity dates (contributions older than ten years)
• Public pension estimate from a vida laboral import
• Early-exit impact on the pension at legal retirement age
• Convenio especial cost vs. pension gained
• Employer and simplified self-employed plans with their higher combined limit
• Spouse contributions and the deduction for them
• Early, partial and delayed retirement options, with reduction and bonus coefficients
• Survivor pensions (widowhood and orphan) as an input to household planning
• Pension contribution gap-filling and the maximum contribution base
Withdrawal planner
• Year-by-year drawdown from FIRE date to age 95, showing which assets to sell, gross amount, tax and net income
• Tax-aware ordering: filling low savings-base brackets, timing pension withdrawals, using a cash buffer
• Bridge view: portfolio needed until pension age, and after it starts
• Configurable spending guardrails after bad years
• Wealth and solidarity tax included in each year's drawdown, including the 60% income-based cap
• Over-65 annuity reinvestment (renta vitalicia) to exempt gains up to €240,000
• IRPF filing-threshold awareness, showing years where no return is needed
• Alternative withdrawal strategies: fixed percentage, VPW, guardrails, floor and ceiling
• Export of the yearly plan as a checklist for each calendar year
Housing and property
• Rent vs. buy, including ITP/VAT, notary, registry, agency and IBI
• Mortgage amortisation, and prepayment vs. investing
• Rental property net yield and rental income tax rules
• Main-home sale: reinvestment exemption and the over-65 exemption
• Grandfathered main-home mortgage deduction (purchases before 2013)
• Imputed income on second homes and empty properties
• Municipal capital-gains tax (plusvalía municipal) on sale or inheritance
• Fixed vs. variable mortgage comparison with Euribor scenarios
• Reverse mortgage and selling the bare ownership (nuda propiedad) as late-life options
Inheritance, gifts and estate (new section)
• Inheritance and gift tax (ISD) by region, kinship group and existing wealth, with regional allowances
• Lifetime gifts to children vs. inheritance, compared on total tax
• Expected inheritances as uncertain future inflows in the FIRE projection
• "Step-up" of cost basis on inherited assets (the IRPF gain resets at death)
• Will and beneficiary tracker: which accounts have named beneficiaries, and where documents are
• Estate summary for heirs: a printable list of accounts, contacts and next steps
Self-employed (autónomos) (new section)
• RETA quota by real-income band, with the year-end adjustment
• Quarterly Modelo 130 and 303 estimates, and money set aside for them
• Business income and deductible expenses kept apart from personal spending
• Contribution base choice vs. future pension, for those who can choose
• Switching from employee to self-employed (or the reverse) as a life event
Insurance and protection (new section)
• Policy register: life, disability, health, home, with premiums and renewal dates
• Protection gap: what the household needs if one earner dies or can't work, vs. cover held
• Emergency fund target in months of essential spending, tracked against liquid assets
• Insurance-linked savings (PIAS, unit-linked) valued as assets
Alerts and reporting
• Milestones: 10/25/50/75/100% of the FIRE number, Coast FIRE reached, one year of expenses saved
• Year-end reminders (pension contribution before 31 December, loss harvesting)
• Modelo 720/721 threshold warnings
• Annual tax summary per user to help prepare the Renta return
• Notification channels: email, ntfy, Gotify, Telegram and mobile push
• Stale-data alerts: account not updated in N days, failed price feed, broken bank sync
• Monthly review: what changed in net worth, why (contributions vs. market), and FIRE-date movement
• Renta check: the app's figures compared line by line with the AEAT draft
• Rule-pack update notice: which of the user's numbers changed when a new pack was installed
• PDF and CSV reports for an adviser or partner
Spanish tax and rules engine
• Versioned rule packs (YAML/JSON) by year and region, with a source link per value
• Covers savings-base brackets, regional general-base scales, personal minimums, pension limits, wealth tax, solidarity tax, Modelo 720/721, Social Security parameters and rental reductions
• Future-year projections use the latest known pack, and the screen says so
• Every tax figure expands to show its base, brackets, deductions and result
• Golden test cases per pack
• Packs installable separately from app upgrades
• Foral regimes (Navarra, Basque Country) as contributor-maintained packs
• Joint filing (tributación conjunta) compared with individual filing (phase 2)
• A visible disclaimer that the figures are an estimate, with a pointer to Renta WEB
• ISD, plusvalía municipal and regional deductions (rent, childcare, donations) added to pack coverage
• Region comparison: the same household's tax in two or more regions
• Canary Islands, Ceuta and Melilla specifics (IGIC, the 60% Ceuta and Melilla deduction)
• Optional special regimes: the inbound-worker ("Beckham") regime and exit tax on leaving Spain
• Charitable donation deduction, including the higher rate for recurring donations
• Assumed inflation of thresholds in future years, as a user setting rather than hard-coded
Data import, migration and quality (new section)
• AEAT datos fiscales import to pre-fill and cross-check the year
• Broker annual tax reports (informe fiscal) imported as a check on lots and gains
• Migration importers: spreadsheet template, Firefly III, Actual Budget, YNAB and Fintonic
• Import preview with undo, so a bad CSV can be rolled back in one step
• Data health page: missing prices, unmatched transfers, lots without cost basis
• Document vault for contracts, broker statements and tax certificates, encrypted like the rest
Security, privacy and ops
• One-command docker compose up deployment, light enough for a Raspberry Pi 4
• Argon2id passwords, TOTP two-factor and optional OIDC (Authelia, Authentik, Keycloak)
• Row-level security with automated cross-user isolation tests
• Encryption in transit and at rest, including backups and connector tokens
• Audit log visible to the affected user
• GDPR data export (JSON and CSV) and account deletion
• Scheduled encrypted backups with a documented restore, tested in CI
• No telemetry, external fonts or trackers by default; all connectors opt-in
• Spanish and English at launch
• WCAG 2.2 AA accessibility
• Documented REST API (OpenAPI) with personal access tokens
• React Native app for iOS and Android
• Passkeys (WebAuthn) as a second factor or password replacement
• Scoped, read-only API tokens and webhooks for events
• Automatic database migrations with a pre-upgrade backup and rollback
• Key management and rotation, with a documented recovery path if the key is lost
• Offline mode and biometric lock on mobile
• Privacy mode that hides amounts on screen (for screen sharing)
• Catalan, Galician and Basque translations
• Dark mode and a light, read-only "glance" view
Open-source and project
• MIT licence, with a public repo and contribution guides
• Separate review process for rule-pack changes
• Signed releases, with an annual release after each year's budget law
• Fictional demo household for screenshots, tests and trying it out
• No affiliate links or product rankings
• "Simulation, not advice" disclaimer on first login
• Security policy with a private disclosure channel and a published threat model
• SBOM and reproducible builds for each release
• Out-of-cycle rule-pack releases when a decree changes figures mid-year
• Guided onboarding wizard and a glossary of Spanish tax terms inside the app
• Public roadmap and governance (who approves rule packs, how maintainers are added)
• Plugin interface for importers and price providers, so contributors don't need core changes