# Generated by Django 4.2.13 on 2024-06-14 22:36

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AttendanceRecord",
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
                ("date", models.DateField()),
                (
                    "status",
                    models.CharField(
                        choices=[("Present", "Present"), ("Absent", "Absent")],
                        max_length=10,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ExtraCurricularActivity",
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
                ("activity_name", models.CharField(max_length=100)),
                ("achievements", models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name="Performance",
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
                ("term", models.CharField(max_length=20)),
                ("year", models.IntegerField()),
                ("teacher_comments", models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name="ReportCard",
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
                ("overall_summary", models.TextField()),
                (
                    "digital_signature_teacher",
                    models.ImageField(blank=True, upload_to="signatures/"),
                ),
                (
                    "digital_signature_principal",
                    models.ImageField(blank=True, upload_to="signatures/"),
                ),
            ],
        ),
    ]
