from django.utils.translation import gettext_lazy as _

from shared_kernel.api.errors import register_messages

register_messages(
    {
        "invalid_email": _("Enter a valid email address."),
        "email_taken": _("An account with this email already exists."),
        "weak_password": _("Use a password of at least 12 characters."),
        "invitation_invalid": _("This invitation link is not valid."),
        "invitation_used": _("This invitation has already been used."),
        "invitation_expired": _("This invitation has expired. Ask for a new one."),
        "invalid_totp_code": _("The code is not valid. Try the current code from your app."),
        "enrolment_invalid": _("This set-up link has expired. Sign up again or ask for help."),
        "invalid_credentials": _("Email or password is not correct."),
        "locked_out": _("Too many failed attempts. Try again in 15 minutes."),
        "mfa_invalid": _("Your sign-in took too long. Start again."),
    }
)
