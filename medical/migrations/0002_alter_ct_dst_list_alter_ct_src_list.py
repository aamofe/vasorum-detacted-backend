# Generated by Django 4.1 on 2024-01-14 08:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("medical", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ct",
            name="dst_list",
            field=models.JSONField(null=True, verbose_name="处理后图片路径"),
        ),
        migrations.AlterField(
            model_name="ct",
            name="src_list",
            field=models.JSONField(null=True, verbose_name="处理前图片路径"),
        ),
    ]
