# Generated by Django 4.1.7 on 2023-04-19 23:26

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("subscription", "0006_alter_filingwebhookevent_status_noop"),
    ]

    operations = [
        migrations.AlterField(
            model_name="filingwebhookevent",
            name="status",
            field=models.SmallIntegerField(
                choices=[
                    (1, "Awaiting processing in queue."),
                    (2, "Item processed successfully."),
                    (3, "Item encountered an error while processing."),
                    (4, "Item is currently being processed."),
                    (5, "Item ignored"),
                    (6, "Awaiting for document purchase"),
                    (7, "Document purchase failed"),
                ],
                default=1,
                help_text="The current status of this upload. Possible values are: (1): Awaiting processing in queue., (2): Item processed successfully., (3): Item encountered an error while processing., (4): Item is currently being processed., (5): Item ignored, (6): Awaiting for document purchase, (7): Document purchase failed",
            ),
        ),
    ]
