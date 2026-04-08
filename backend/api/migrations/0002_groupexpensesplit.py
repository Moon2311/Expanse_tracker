# Generated manually for GroupExpenseSplit

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="GroupExpenseSplit",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "share_amount",
                    models.DecimalField(decimal_places=2, max_digits=12),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("pending", "Pending"), ("paid", "Paid")],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("paid_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "expense",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="splits",
                        to="api.expense",
                    ),
                ),
                (
                    "owee",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="group_expense_splits_owed",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["created_at"],
            },
        ),
        migrations.AlterUniqueTogether(
            name="groupexpensesplit",
            unique_together={("expense", "owee")},
        ),
    ]
