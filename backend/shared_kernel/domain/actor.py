"""Who is acting. Every tenant-scoped read or write is done on behalf of an Actor."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class Actor:
    user_id: UUID
    is_admin: bool
