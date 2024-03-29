# Generated by Django 4.2.1 on 2023-07-20 13:01

import django.db.models.deletion
from django.db import migrations, models

import drf_kit.models.diff_models
import drf_kit.models.file_models


class Migration(migrations.Migration):
    dependencies = [
        ("test_app", "0007_beast_beast_test_app_be_updated_682cc9_idx_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="BeastOwner",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="created at")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="updated at")),
                ("deleted_at", models.DateTimeField(blank=True, default=None, null=True, verbose_name="deleted at")),
                ("name", models.CharField(max_length=100)),
            ],
            options={
                "ordering": ("-updated_at",),
                "get_latest_by": "updated_at",
                "abstract": False,
            },
            bases=(
                drf_kit.models.diff_models.ModelDiffMixin,
                drf_kit.models.file_models.BoundedFileMixin,
                models.Model,
            ),
        ),
        migrations.CreateModel(
            name="BeastOwnership",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="created at")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="updated at")),
                ("deleted_at", models.DateTimeField(blank=True, default=None, null=True, verbose_name="deleted at")),
                (
                    "beast",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="ownerships",
                        to="test_app.beast",
                    ),
                ),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="test_app.beastowner")),
            ],
            options={
                "ordering": ("-updated_at",),
                "get_latest_by": "updated_at",
                "abstract": False,
            },
            bases=(
                drf_kit.models.diff_models.ModelDiffMixin,
                drf_kit.models.file_models.BoundedFileMixin,
                models.Model,
            ),
        ),
        migrations.AddField(
            model_name="beastowner",
            name="beasts",
            field=models.ManyToManyField(related_name="owners", through="test_app.BeastOwnership", to="test_app.beast"),
        ),
        migrations.AddIndex(
            model_name="beastownership",
            index=models.Index(fields=["updated_at"], name="test_app_be_updated_2edab0_idx"),
        ),
        migrations.AddIndex(
            model_name="beastownership",
            index=models.Index(fields=["deleted_at"], name="test_app_be_deleted_bdecc0_idx"),
        ),
        migrations.AddIndex(
            model_name="beastowner",
            index=models.Index(fields=["updated_at"], name="test_app_be_updated_0c853e_idx"),
        ),
        migrations.AddIndex(
            model_name="beastowner",
            index=models.Index(fields=["deleted_at"], name="test_app_be_deleted_19fd8c_idx"),
        ),
    ]
