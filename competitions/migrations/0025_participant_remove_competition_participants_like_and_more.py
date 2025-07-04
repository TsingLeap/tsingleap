# Generated by Django 5.1.7 on 2025-05-19 10:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("competitions", "0024_competition_tags"),
        ("users", "0003_alter_user_nickname"),
    ]

    operations = [
        migrations.CreateModel(
            name="Participant",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=255)),
                ("score", models.IntegerField(default=0)),
            ],
        ),
        migrations.RemoveField(
            model_name="competition",
            name="participants",
        ),
        migrations.CreateModel(
            name="Like",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="users.user"
                    ),
                ),
                (
                    "participant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="competitions.participant",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="competition",
            name="participants",
            field=models.ManyToManyField(
                blank=True, related_name="competition", to="competitions.participant"
            ),
        ),
    ]
