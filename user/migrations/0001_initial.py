# Generated by Django 4.1 on 2024-01-14 02:31

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="User",
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
                ("doctor_id", models.CharField(max_length=10, unique=True)),
                ("username", models.CharField(max_length=20, verbose_name="昵称")),
                ("password", models.CharField(max_length=20, verbose_name="密码")),
            ],
        ),
    ]
