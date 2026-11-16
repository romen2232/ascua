"""Create the first admin of a fresh instance and print their TOTP enrolment details."""

import getpass
import uuid
from typing import Any

from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.utils import timezone

from identity.application.sign_up import MIN_PASSWORD_LENGTH
from identity.domain.email import Email
from identity.domain.user import User
from identity.infrastructure.models import UserRecord
from identity.infrastructure.repositories import DjangoUserRepository
from identity.infrastructure.tokens import SignedEnrolmentTokens
from identity.infrastructure.totp import DjangoOtpTotp


class Command(BaseCommand):
    help = "Create the first admin user. Refuses to run once any user exists."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--email", required=True)
        parser.add_argument("--display-name", default="Admin")
        parser.add_argument("--password", help="Prompted for when omitted.")

    def handle(self, *args: Any, **options: Any) -> None:
        if UserRecord.objects.exists():
            raise CommandError("This instance already has users; invite new ones instead.")
        password = options["password"] or getpass.getpass("Password: ")
        if len(password) < MIN_PASSWORD_LENGTH:
            raise CommandError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")
        user = User(
            id=uuid.uuid4(),
            email=Email(options["email"]),
            display_name=options["display_name"],
            locale="es",
            is_admin=True,
            totp_confirmed=False,
            created_at=timezone.now(),
        )
        DjangoUserRepository().add(user, password)
        uri = DjangoOtpTotp().create_device(user.id)
        token = SignedEnrolmentTokens().issue(user.id)
        self.stdout.write(f"Admin {user.email} created.")
        self.stdout.write(f"Add this to your authenticator app: {uri}")
        self.stdout.write(f"Enrolment token (valid 15 minutes): {token}")
