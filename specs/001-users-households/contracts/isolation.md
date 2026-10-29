# Contract: Isolation Rules and Test Registry

**Feature**: 001-users-households | **Requirements**: NF-3, USR-5, FR-014 to FR-017, SC-002, SC-003

This is the contract every current and future endpoint, model and background task must satisfy.
It applies to all later specs.

## Rules for code

1. A tenant model (any model holding personal or financial data) MUST:
   - use `TenantManager` as its default manager (unscoped queries raise `UnscopedQueryError`);
   - have an RLS policy migration created with the `enable_rls(...)` migration helper;
   - be covered by an export section (or a documented exclusion) and by deletion.
2. A view touching tenant data MUST subclass `ScopedViewSet` / `ScopedAPIView`, which take the
   `Actor` from the request and refuse to run without one.
3. A Celery task touching tenant data MUST receive an actor id and run its body inside
   `actor_context(actor)`. System tasks use `system_context(reason=...)`, which is limited to an
   allow-list of tables and operations in `core/rls/system_allowlist.py`.
4. Raw SQL against tenant tables is allowed only inside a transaction where the RLS context is set.
5. Responses MUST use `404 not_found` for anything the actor cannot read.

## Test registry

`backend/tests/isolation/registry.py` maps every route (method + path pattern from the OpenAPI
schema) to an `IsolationCase`:

```python
IsolationCase(
    route="GET /api/v1/me/profile/dependants/{id}",
    setup=fixtures.dependant_of_user_b,   # creates the target owned by "victim" B
    allowed=[Role.OWNER],                  # who may succeed
    denied=[Role.OTHER_USER, Role.OTHER_HOUSEHOLD_MEMBER, Role.ADMIN_NO_GRANT,
            Role.PAT_OTHER_USER, Role.HOUSEHOLD_VIEWER],
    expect_denied_status=404,
)
```

The suite builds a fixed world for each case: users A and B in household H1, user C in household
H2, admin D, a viewer V in H1, and PATs for each user. It then runs the request as every role.

**Build-breaking checks**
- A route in the OpenAPI schema with no `IsolationCase` (or an explicit `public=True` marker for
  anonymous auth routes).
- A tenant model without an RLS policy, export coverage or deletion coverage.
- Any denied role receiving a 2xx, a different status than the case declares, or a body or headers
  that differ between "exists but denied" and "does not exist".

## Database-level checks

For each tenant table, a test inserts rows as `ascua_owner`, connects as `ascua_app`, sets the
context of a different actor, and asserts:
- `SELECT` returns zero rows;
- `UPDATE` and `DELETE` affect zero rows;
- `INSERT` with a foreign `user_id` fails the policy check;
- with no context set at all, `SELECT` returns zero rows (fail closed).
