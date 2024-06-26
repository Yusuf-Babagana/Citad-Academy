# Generated by Django 4.2.13 on 2024-06-14 22:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("school_management", "0001_initial"),
        ("media_management", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="media",
            name="school",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="school_management.school",
            ),
        ),
        migrations.AddField(
            model_name="comment",
            name="media",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="comments",
                to="media_management.media",
            ),
        ),
    ]
