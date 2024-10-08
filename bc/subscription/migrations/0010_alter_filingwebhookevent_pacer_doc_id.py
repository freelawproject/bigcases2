# Generated by Django 5.0.8 on 2024-09-05 16:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("subscription", "0009_subscription_article_url"),
    ]

    operations = [
        migrations.AlterField(
            model_name="filingwebhookevent",
            name="pacer_doc_id",
            field=models.CharField(
                blank=True,
                help_text="The ID of the document in PACER.",
                max_length=64,
            ),
        ),
    ]
