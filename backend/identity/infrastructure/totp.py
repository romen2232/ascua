"""TOTP through django-otp: 30-second steps, 6 digits, ±1 step drift, no code reuse."""

from uuid import UUID

from django_otp.plugins.otp_totp.models import TOTPDevice


class DjangoOtpTotp:
    def create_device(self, user_id: UUID) -> str:
        TOTPDevice.objects.filter(user_id=user_id).delete()
        device = TOTPDevice.objects.create(
            user_id=user_id, name="ascua", confirmed=False, step=30, digits=6, tolerance=1
        )
        return str(device.config_url)

    def verify(self, user_id: UUID, code: str) -> bool:
        device = TOTPDevice.objects.filter(user_id=user_id).first()
        return bool(device and device.verify_token(code))
