# Generated by Django 5.1.7 on 2025-04-24 17:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("forum", "0008_migrate_post_to_generic"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="comment",
            name="post",
        ),
    ]
