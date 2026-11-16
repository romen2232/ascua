# Plan 1 (Foundation): decisions made during implementation

Every deviation from or addition to `2026-11-16-01-foundation.md`, with its reason and cost if wrong, followed by the final review outcome. Recorded during inline execution on 2026-11-16.

## Rulings

- Setup: Ruling: work on branch feat/foundation in the main checkout instead of a separate worktree — the plan's Task 1 commits uncommitted working-tree changes (spec-kit removal, docs) that a fresh worktree would not have — cost if wrong: none, branch is isolated from main.
- Task 1: Ruling: dev Postgres on host port 5442 — 5432 is taken by another local project — cost if wrong: none, env-overridable.
- Task 1: Ruling: app-role grants live in shared_kernel migration 0001 instead of only the init SQL — test databases don't inherit per-database default privileges — cost if wrong: none.
- Task 1: Ruling: added test_tests_run_as_runtime_role — ascua_owner is also NOBYPASSRLS so the plan's smoke test couldn't detect a missing SET ROLE; verified RED then GREEN.
- Task 3: Ruling: fixture seeds rows by acting as each owner, not as ascua_owner — FORCE RLS applies to the table owner too, so the plan's approach cannot insert — cost if wrong: none.
- Task 3: Ruling: acting_as restores the previous actor on exit (plus test) — transaction-local settings otherwise outlive the block inside an outer transaction (e.g. ATOMIC_REQUESTS) — cost if wrong: actor leaks within one request.
- Task 3: Ruling: actor context also stores is_admin (ascua.actor_is_admin) so current_actor() can return a full Actor — cost if wrong: none.
- Task 3: Ruling: test DB grants TRUNCATE to ascua_app (test-only) so transactional tests can flush — cost if wrong: none outside tests.
- Task 3: Ruling: two_users_with_notes lives in tests/conftest.py (shared by isolation and shared_kernel tests) instead of tests/isolation/conftest.py.
- Task 4: Ruling: PermissionDenied is mapped to 404 not_found in the error handler — Global Constraints say denied access is 404, never 403 — cost if wrong: none.
- Task 4: Ruling: ScopedViewSet clears the actor in finalize_response (added clear_actor + test) — prevents an actor surviving past its request inside a shared transaction — cost if wrong: none.
- Task 4: Ruling: Actor.is_admin read via getattr(user, "is_admin", False) until Task 7 adds the field; shared_kernel must not import identity — cost if wrong: admins treated as non-admin until Task 7 (safe direction).
- Task 4: Ruling: JWTAuthentication + IsAuthenticated set as DRF defaults now so unauthenticated gives 401; test URLs via ROOT_URLCONF=tests.urls (test settings only).
- Task 4: Ruling: ModelSerializer.save() is unusable on tenant models (default manager refuses unscoped queries); creates go through for_actor()/repositories — intended guardrail.
- Task 5: Ruling: RouteCase gains `collection` and `write_payload`; collection routes check the owner's item id is absent from the intruder's 200 response, and POST to a collection is not an isolation case (it creates for the caller) — cost if wrong: a collection write that targets other users would be missed.
- Task 5: Ruling: admin variant sets is_admin on the user instance until Task 7 adds the field.
- Task 5: Ruling: added test_registry_has_no_stale_routes and test_exemptions_point_at_real_models so the registry can't silently rot.
- Task 6: Ruling: an invitation is valid up to and including expires_at (expired only when now > expires_at); 'used' is checked before 'expired' — cost if wrong: one second of extra validity.
- Task 7: Ruling: migration 0002 hand-written (makemigrations prompts for created_at on existing rows); verified with makemigrations --check — cost if wrong: none.
- Task 7: Ruling: InvitationRecord.invited_by is a PROTECT foreign key to the user (not a bare UUID) — keeps referential integrity; an admin with issued invitations cannot be hard-deleted until GDPR deletion (plan 9) handles it.
- Task 8: Ruling: confirm_totp takes the enrolment token (not a user id) and rejects a second confirmation — the token is what proves who is enrolling; an already-confirmed user can't re-enrol through it — cost if wrong: none.
- Task 8: Ruling: added WeakPassword (min 12 chars, MIN_PASSWORD_LENGTH in identity.application.sign_up), display-name and locale validation in accept_invitation; invite_user rejects emails that already have an account (409).
- Task 8: Ruling: added registry kind "admin" with test_admin_routes_are_not_found_for_non_admins — invitation-create is neither tenant nor public.
- Task 8: Ruling: SignUpDeps groups the ports (identity.application.deps) instead of passing five positional arguments.
- Task 8: Ruling: ascua_init takes --password (prompts when omitted) and prints the enrolment token, so the first admin can confirm TOTP through /api/auth/totp/confirm.
- Task 9: Ruling: DomainError gains `rollback` (default True); InvalidCredentials and LockedOut set False — the API error handler otherwise rolls back the request transaction and erases django-axes failure records, so lockout never triggers. Test: test_domain_error_without_rollback_keeps_writes — cost if wrong: a non-rollback error could commit partial writes; only those two errors use it, and the password step writes nothing else.
- Task 9: Ruling: lockout triggers on the 5th failed password (django-axes locks at FAILURE_LIMIT), so the 5th wrong attempt already returns 429; test adjusted, behaviour matches "5 failures / 15 min" — cost if wrong: none.
- Task 9: Ruling: credentials passed to authenticate() as email= (USERNAME_FIELD) because django-axes keys lockouts by that field; with username= every failure was recorded with a null username.
- Task 9: Ruling: TOTP-not-enrolled is reported at the password step (after a correct password) rather than the TOTP step.
- Task 9: Ruling: refresh/sign-out views declare a Bearer authenticate header so invalid tokens give 401 instead of DRF's 403.
- Task 9: Ruling: test/dev SECRET_KEY lengthened to ≥32 bytes (PyJWT warns on short HMAC keys); production key comes from ASCUA_SECRET_KEY.
- Task 9: Ruling: error messages are registered per context (register_messages; identity/api/messages.py) instead of one central dict.
- Task 10: Ruling: the user's locale fallback is applied in the API exception handler (JWT auth runs inside the view, after LocaleMiddleware); explicit Accept-Language still wins — tested both ways.
- Task 10: Ruling: msgids are English source strings; .mo files are git-ignored and compiled by scripts/check.sh (and documented in CLAUDE.md) — cost if wrong: a deploy without compilemessages shows English; the ops plan's image build must run it.
- Task 10: Ruling: added test_every_error_message_is_in_the_catalog so a new error code without a catalog entry fails the build.
- Task 11: Ruling: removed the template's app/.claude/settings.json (enabled a plugin), app/AGENTS.md and Expo's LICENSE (wrong copyright for this project) — cost if wrong: none; licence choice stays on the roadmap.
- Task 11: Ruling: started from blank-typescript and added expo-router by hand (main = expo-router/entry) instead of the default template's demo tabs.
- Task 11: Ruling: openapi-typescript 7.13 only declares TypeScript ^5; npm `overrides` runs it against the project's TypeScript 6 (build-time generator only) — cost if wrong: type generation breaks on a TS change; drift guard in check.sh would catch it.
- Task 11: Ruling: tsconfig lists types ["jest"] (TypeScript 6 no longer auto-includes @types); lint is `eslint . --max-warnings 0`.
- Task 11: Ruling: schema.d.ts is committed; backend/openapi.json is generated and git-ignored; check.sh regenerates both and fails on drift (git diff --exit-code).
- Task 11: Ruling: client exposes createApiClient(options) for tests plus a default `api` whose token handlers are registered by the session module (setAuthHandlers); auth endpoints never trigger a refresh.
- Task 11: Ruling: "renders on web" verified with `expo export --platform web` (bundle builds) instead of a dev server.
- Task 12: Ruling: screens live in src/screens with thin route files in app/ — expo-router turns every file under app/ (including __tests__) into a route; tests are src/screens/__tests__/screens.test.tsx and src/auth/__tests__/session.test.ts.
- Task 12: Ruling: added django-cors-headers (backend, with tests): web client origin from ASCUA_CORS_ORIGINS (dev default http://localhost:8081), credentials allowed, X-Ascua-Client header allowed — required for the cookie-based web refresh.
- Task 12: Ruling: the client translates API error codes itself (errors.<code> keys, fallback errors.unknown) rather than showing the server message, so UI language is consistent.
- Task 12: Ruling: session exposes createSession({storage}) + a singleton wired to `api`; concurrent 401s share one refresh promise.
- Task 12: Ruling: the plan's manual browser/emulator check was replaced by an HTTP end-to-end run against runserver on the migrated dev DB (admin init → TOTP → sign-in → invite → sign-up → web sign-in cookie → reuse rejected → Spanish error): all passed. Web bundle verified by `expo export` in Task 11. No device/emulator check was done — cost if wrong: a native-only rendering issue would surface at first device run.
- Task 13: Ruling: CI creates the DB roles with psql from docker/postgres/init/01-roles.sql against a postgres:17 service on port 5442, installs gettext (compilemessages), and runs scripts/check.sh — the workflow has NOT run on GitHub yet (nothing pushed) — cost if wrong: first push may need a CI fix.
- Final: Ruling: reviewer declined to judge account-lockout DoS from the attacker's own IP — lockout is keyed on email+IP, so an attacker can only lock that email from their own IP; the real user elsewhere is unaffected — stands — cost if wrong: none.
- Final: Ruling: reviewer declined production settings/compose, GDPR deletion vs PROTECT FK, native-device rendering, licence choice, 1-second expiry boundary — all already ruled or out of plan 1; they stand and are listed for the owner.

## Final review

- Final review: fresh reviewer (opus) on d86f674..c9264cc — verdict "with fixes": 2 Critical, 2 Important, 4 Minor.
- Final: fixed TOTP throttling rolled back by the error handler — test_wrong_totp_codes_are_throttled RED→GREEN (InvalidTotpCode.rollback=False), suite 120/120.
- Final: fixed web sign-out could not revoke the cookie session (cookie Path=/api/auth/refresh never sent to /api/auth/sign-out; plan defect) — test_refresh_cookie_reaches_refresh_and_sign_out, test_web_sign_out_revokes_cookie_session, test_sign_out_without_token_still_clears_cookie RED→GREEN, suite 123/123.
- Final: fixed concurrent accept of one invitation → 500 — test_invitation_lookup_locks_the_row RED→GREEN (select_for_update), suite 124/124.
- Final: fixed accounts stranded after missing the 15-minute TOTP window (incl. first admin) — test_unconfirmed_user_gets_fresh_enrolment_at_sign_in RED→GREEN; client: session "enrol" state + EnrolScreen, 3 new client tests RED→GREEN; suites 125/125 backend, 23/23 client. TotpNotEnrolled error removed.
- Final: plan doc amended (cookie path, unenrolled sign-in).
- Final: minor (deferred): manage.py/wsgi.py default to dev settings (DEBUG, known SECRET_KEY default) — production settings module belongs to the ops plan.
- Final: minor (deferred): TenantManager.all_unscoped_for_system uses inspect.stack() (slow, heuristic); RLS still protects data.
- Final: minor (deferred): an unconfirmed user's enrolment token can be replayed within 15 minutes after a new device is created; harmless today.
- Final: minor (deferred): CI workflow has never run on GitHub.
