# Generated by Django 4.1.3 on 2022-12-29 03:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rtrsApp', '0011_rename_station_id_cost_station_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='booked_seat',
            old_name='train_id',
            new_name='train',
        ),
    ]
