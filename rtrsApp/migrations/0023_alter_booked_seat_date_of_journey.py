# Generated by Django 4.1.3 on 2023-01-01 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rtrsApp', '0022_remove_booked_seat_from_station_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booked_seat',
            name='date_of_journey',
            field=models.DateTimeField(),
        ),
    ]
