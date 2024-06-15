# Generated by Django 4.2.13 on 2024-06-14 22:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("student_management", "0001_initial"),
        ("class_management", "0001_initial"),
        ("leaderboard", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="leaderboard",
            name="student",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="leaderboards",
                to="student_management.student",
            ),
        ),
        migrations.AddField(
            model_name="leaderboard",
            name="subject",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="leaderboards",
                to="class_management.subject",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="leaderboard",
            unique_together={("student", "subject", "classroom", "exam", "school")},
        ),
    ]