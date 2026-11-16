from collections.abc import Callable

from identity.application.deps import SignUpDeps
from identity.domain.email import Email
from identity.domain.errors import EmailTaken
from identity.domain.invitation import Invitation
from shared_kernel.domain.actor import Actor
from shared_kernel.domain.errors import NotAllowed


def invite_user(
    actor: Actor, email: Email, deps: SignUpDeps, token_factory: Callable[[], str]
) -> str:
    """Issue an invitation and return the raw token (shown once, never stored)."""
    if not actor.is_admin:
        raise NotAllowed
    if deps.users.get_by_email(email) is not None:
        raise EmailTaken
    invitation, raw = Invitation.issue(email, actor.user_id, deps.clock.now(), token_factory)
    deps.invitations.add(invitation)
    return raw
