# Generated by Django 4.1.3 on 2022-12-30 05:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rtrsApp', '0018_rename_payment_id_mobile_banking_payment'),
    ]

    operations = [
        migrations.RenameField(
            model_name='booked_seat',
            old_name='reservation_id',
            new_name='reservation',
        ),
    ]
