# Generated by Django 5.1.1 on 2025-04-09 14:22

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("meds", "0053_rename_quantity_per_dose_medicine_duration_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="appointment",
            name="created_at",
            field=models.DateTimeField(
                default=datetime.datetime(2025, 4, 9, 19, 51, 59, 737210)
            ),
        ),
    ]
