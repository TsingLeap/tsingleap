# Generated by Django 5.1.7 on 2025-05-21 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tag", "0005_alter_tag_tag_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tag",
            name="tag_type",
            field=models.CharField(
                choices=[
                    ("sports", "运动"),
                    ("department", "院系"),
                    ("event", "赛事"),
                    ("highlight", "精华帖"),
                    ("default", "默认"),
                ],
                default="default",
                max_length=32,
            ),
        ),
    ]
