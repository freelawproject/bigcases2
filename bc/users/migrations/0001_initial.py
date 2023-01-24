# Generated by Django 4.1.5 on 2023-01-19 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="User",
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
                    "password",
                    models.CharField(max_length=128, verbose_name="password"),
                ),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "date_created",
                    models.DateTimeField(
                        auto_now_add=True,
                        db_index=True,
                        help_text="The moment when the item was created.",
                    ),
                ),
                (
                    "date_modified",
                    models.DateTimeField(
                        auto_now=True,
                        db_index=True,
                        help_text="The last moment when the item was modified. A value in year 1750 indicates the value is unknown",
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        help_text="The email address of the user.",
                        max_length=254,
                        unique=True,
                    ),
                ),
                ("affiliation", models.TextField()),
                ("enabled", models.BooleanField(default=False)),
                ("allow_login", models.BooleanField(default=False)),
                ("allow_spend", models.BooleanField(default=False)),
                ("allow_follow", models.BooleanField(default=False)),
            ],
            options={
                "abstract": False,
            },
        ),
    ]