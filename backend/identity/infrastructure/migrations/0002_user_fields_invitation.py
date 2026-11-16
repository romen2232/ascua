import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("identity", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="userrecord",
            name="display_name",
            field=models.CharField(default="", max_length=100),
        ),
        migrations.AddField(
            model_name="userrecord",
            name="locale",
            field=models.CharField(
                choices=[("es", "es"), ("en", "en")], default="es", max_length=2
            ),
        ),
        migrations.AddField(
            model_name="userrecord",
            name="is_admin",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="userrecord",
            name="totp_confirmed",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="userrecord",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name="InvitationRecord",
            fields=[
                ("id", models.UUIDField(editable=False, primary_key=True, serialize=False)),
                ("email", models.EmailField(max_length=254)),
                ("token_hash", models.CharField(max_length=64, unique=True)),
                ("expires_at", models.DateTimeField()),
                ("used_at", models.DateTimeField(null=True)),
                (
                    "invited_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"db_table": "identity_invitation"},
        ),
    ]
