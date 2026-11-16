import uuid

from django.db import migrations, models

from shared_kernel.infrastructure.rls import EnableRLS


class Migration(migrations.Migration):
    initial = True
    dependencies = [("shared_kernel", "0001_grant_app_role")]
    operations = [
        migrations.CreateModel(
            name="SampleNote",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ("owner_id", models.UUIDField()),
                ("text", models.CharField(max_length=200)),
            ],
        ),
        EnableRLS("samplenote"),
    ]
