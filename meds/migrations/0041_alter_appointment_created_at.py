# Generated by Django 5.1.1 on 2025-04-04 18:32

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("meds", "0040_alter_appointment_created_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="appointment",
            name="created_at",
            field=models.DateTimeField(
                default=datetime.datetime(2025, 4, 5, 0, 2, 32, 82700)
            ),
        ),
    ]
