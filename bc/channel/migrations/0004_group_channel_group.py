# Generated by Django 4.1.7 on 2023-05-05 20:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sponsorship", "0002_sponsorship_watermark_message"),
        ("channel", "0003_alter_channel_user"),
    ]

    operations = [
        migrations.CreateModel(
            name="Group",
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
                    "name",
                    models.CharField(
                        help_text="Name for a set of channels", max_length=100
                    ),
                ),
                (
                    "is_big_cases",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether this group should be treated as the set of big cases channels",
                    ),
                ),
                (
                    "sponsorships",
                    models.ManyToManyField(
                        blank=True,
                        related_name="groups",
                        to="sponsorship.sponsorship",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="channel",
            name="group",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="channels",
                to="channel.group",
            ),
        ),
    ]
