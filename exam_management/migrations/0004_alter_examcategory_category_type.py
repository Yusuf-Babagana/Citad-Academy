# Generated by Django 4.2.13 on 2024-06-21 10:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("exam_management", "0003_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="examcategory",
            name="category_type",
            field=models.CharField(
                choices=[
                    ("CITAD", "CENTER FOR INFORMATION TECHNOLOGY AND DEVELOPMENT"),
                    ("POLY", "Polytechnic"),
                    ("COE", "College of Education"),
                    ("WAEC", "WAEC"),
                    ("NECO", "NECO"),
                    ("JAMB", "JAMB"),
                ],
                default="CITAD",
                max_length=100,
            ),
        ),
    ]
