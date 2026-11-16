from dataclasses import dataclass
from datetime import datetime
from typing import Literal
from uuid import UUID

from identity.domain.email import Email

Locale = Literal["es", "en"]


@dataclass
class User:
    id: UUID
    email: Email
    display_name: str
    locale: Locale
    is_admin: bool
    totp_confirmed: bool
    created_at: datetime
