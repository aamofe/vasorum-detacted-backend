# Generated by Django 5.0.4 on 2024-04-11 03:28

import django.db.models.deletion
import medical.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("medical", "0004_ct_diagnosis_patient_docter_patient_latest_ct_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Segmenteation",
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
                    "img",
                    models.ImageField(upload_to=medical.models.seg_upload_to),
                ),
                (
                    "path",
                    models.CharField(default="src", max_length=20, verbose_name="上传路径"),
                ),
                (
                    "photo",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="小图",
                        to="medical.photo",
                    ),
                ),
            ],
        ),
    ]
