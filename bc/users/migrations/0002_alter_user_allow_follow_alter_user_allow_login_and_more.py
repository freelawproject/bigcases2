# Generated by Django 4.1.5 on 2023-01-20 12:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="allow_follow",
            field=models.BooleanField(
                default=False,
                help_text="Whether to allow commanding BCB to follow a caseDisabled by default; unless allow_spend is also set",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="allow_login",
            field=models.BooleanField(
                default=False,
                help_text="Whether to allow login to the appDisabled by default; must enable manually",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="allow_spend",
            field=models.BooleanField(
                default=False,
                help_text="Whether to allow purchasing a docketDisabled by default; must enable manually",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="enabled",
            field=models.BooleanField(
                default=False,
                help_text="Overall enable switch. Disable to shut out account entirely.Disabled by default; must enable manually",
            ),
        ),
    ]
