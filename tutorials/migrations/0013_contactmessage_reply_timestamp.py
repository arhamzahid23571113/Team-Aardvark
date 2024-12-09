# Generated by Django 5.1.2 on 2024-12-08 23:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutorials', '0012_contactmessage_reply'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactmessage',
            name='reply_timestamp',
            field=models.DateTimeField(blank=True, help_text="Timestamp of admin's reply", null=True),
        ),
    ]