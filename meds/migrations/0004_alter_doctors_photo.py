# Generated by Django 5.1.1 on 2024-10-14 16:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("meds", "0003_customuser_dob_customuser_gender_doctors_photo"),
    ]

    operations = [
        migrations.AlterField(
            model_name="doctors",
            name="photo",
            field=models.ImageField(
                default="user-avatar.png", upload_to="static/profile_photos"
            ),
        ),
    ]
