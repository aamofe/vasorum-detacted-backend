# Generated by Django 5.0.4 on 2024-04-11 11:40

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("medical", "0007_rename_segmenteation_segmentation"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="patient",
            name="latest_ct",
        ),
    ]
