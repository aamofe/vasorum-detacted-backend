# Generated by Django 5.0.4 on 2024-04-15 07:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("medical", "0011_ct_comment"),
    ]

    operations = [
        migrations.AddField(
            model_name="patient",
            name="latest_ct",
            field=models.DateTimeField(null=True, verbose_name="最近一次ct的时间"),
        ),
    ]
