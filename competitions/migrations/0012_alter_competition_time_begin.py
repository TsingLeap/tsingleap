# Generated by Django 5.1.7 on 2025-04-24 17:15

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("competitions", "0011_alter_competition_time_begin"),
    ]

    operations = [
        migrations.AlterField(
            model_name="competition",
            name="time_begin",
            field=models.DateTimeField(
                default=datetime.datetime(2025, 4, 24, 17, 15, 35, 528625)
            ),
        ),
    ]
