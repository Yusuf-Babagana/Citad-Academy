# Generated by Django 4.2.13 on 2024-06-14 22:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("class_management", "0001_initial"),
        ("exam_management", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Leaderboard",
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
                ("score", models.DecimalField(decimal_places=2, max_digits=5)),
                ("rank", models.PositiveIntegerField(null=True)),
                ("is_independent_learner", models.BooleanField(default=False)),
                (
                    "classroom",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="leaderboards",
                        to="class_management.class",
                    ),
                ),
                (
                    "exam",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="leaderboards",
                        to="exam_management.exam",
                    ),
                ),
            ],
        ),
    ]