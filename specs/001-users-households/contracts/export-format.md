# Contract: ascua Export Format v1

**Feature**: 001-users-households | **Requirement**: NF-6, FR-032

An export is a ZIP archive named `ascua-export-<YYYYMMDDTHHMMSSZ>.zip` containing:

```
export.json          # complete, machine-readable; the authoritative copy
csv/<section>.csv    # one file per section, for spreadsheets
README.txt           # what each file is, in the user's language
```

## export.json

```json
{
  "format": "ascua-export",
  "format_version": 1,
  "generated_at": "2026-10-29T12:00:00Z",
  "instance_version": "0.1.0",
  "user_id": "0192…",
  "sections": {
    "user": { … },
    "tax_profile": { … },
    "region_history": [ … ],
    "dependants": [ … ],
    "social_security": { … },
    "household_memberships": [ … ],
    "household_goals": [ … ],
    "ownership_shares": [ … ],
    "sharing_settings": [ … ],
    "viewer_grants_given": [ … ],
    "viewer_grants_received": [ … ],
    "support_grants": [ … ],
    "access_log": [ … ],
    "personal_access_tokens": [ … ],
    "sessions": [ … ],
    "notifications": [ … ]
  }
}
```

## Rules

- **Scope**: the user's own rows; their shares and settings on items; and, for items they co-own,
  only the item id and their share. Never other users' personal data beyond the display name of
  co-owners and household members they already see.
- **Excluded**: password hashes, TOTP secrets, recovery codes, token hashes, invitation tokens. The
  README lists these exclusions.
- **Types**: ids are UUID strings; timestamps are ISO 8601 UTC; dates are `YYYY-MM-DD`; percentages
  are integer basis points (`share_bp`); money is integer cents in fields ending `_cents`, with a
  sibling `currency` where relevant.
- **CSV**: UTF-8 with BOM (opens correctly in Excel), comma separator, header row, one file per
  JSON section that is a list; nested objects are flattened with `.`.
- **Versioning**: adding a section or field is a minor change and keeps `format_version`. Renaming,
  removing or changing the meaning of a field increments `format_version`. A JSON Schema per
  version is published in `backend/apps/privacy/schemas/export-v<N>.json`, and every export is
  validated against it in tests.
- **Extension**: later features add sections by registering an `ExportSection`; the schema and this
  document are updated in the same change.
