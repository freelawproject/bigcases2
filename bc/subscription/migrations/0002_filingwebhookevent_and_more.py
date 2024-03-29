# Generated by Django 4.1.6 on 2023-02-08 00:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("subscription", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="FilingWebhookEvent",
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
                    "docket_id",
                    models.IntegerField(
                        help_text="The docket id from CL.", null=True
                    ),
                ),
                (
                    "pacer_doc_id",
                    models.CharField(
                        blank=True,
                        help_text="The ID of the document in PACER.",
                        max_length=32,
                    ),
                ),
                (
                    "document_number",
                    models.BigIntegerField(
                        blank=True,
                        help_text="The docket entry number for the document.",
                        null=True,
                    ),
                ),
                (
                    "attachment_number",
                    models.SmallIntegerField(
                        blank=True,
                        help_text="If the file is an attachment, the number is the attachment number on the docket.",
                        null=True,
                    ),
                ),
                (
                    "status",
                    models.SmallIntegerField(
                        choices=[
                            (1, "Awaiting processing in queue."),
                            (2, "Item processed successfully."),
                            (3, "Item encountered an error while processing."),
                            (4, "Item is currently being processed."),
                        ],
                        default=1,
                        help_text="The current status of this upload. Possible values are: (1): Awaiting processing in queue., (2): Item processed successfully., (3): Item encountered an error while processing., (4): Item is currently being processed.",
                    ),
                ),
                (
                    "subscription",
                    models.ForeignKey(
                        help_text="The subscription that was updated by this request.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="subscription.subscription",
                    ),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name="filingwebhookevent",
            index=models.Index(
                fields=["docket_id"], name="subscriptio_docket__82545e_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="filingwebhookevent",
            index=models.Index(
                fields=["pacer_doc_id"], name="subscriptio_pacer_d_c5922a_idx"
            ),
        ),
    ]
