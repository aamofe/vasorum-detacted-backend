# Generated by Django 5.0.4 on 2024-04-15 06:39

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("medical", "0008_remove_patient_latest_ct"),
    ]

    operations = [
        migrations.AddField(
            model_name="ct",
            name="model_url",
            field=models.URLField(null=True, verbose_name="模型路径"),
        ),
    ]