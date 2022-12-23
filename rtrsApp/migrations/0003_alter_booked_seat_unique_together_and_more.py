# Generated by Django 4.1.3 on 2022-12-19 18:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rtrsApp', '0002_alter_station_table'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='booked_seat',
            unique_together={('train_id', 'seat_no', 'reservation_id')},
        ),
        migrations.AlterModelTable(
            name='booked_seat',
            table='booked_seat',
        ),
        migrations.AlterModelTable(
            name='card',
            table='Card',
        ),
        migrations.AlterModelTable(
            name='cost',
            table='cost',
        ),
        migrations.AlterModelTable(
            name='mobile_banking',
            table='Mobile_Banking',
        ),
        migrations.AlterModelTable(
            name='nexuspay',
            table='Nexuspay',
        ),
        migrations.AlterModelTable(
            name='r_user',
            table='r_user',
        ),
        migrations.AlterModelTable(
            name='reservation',
            table='Reservation',
        ),
        migrations.AlterModelTable(
            name='train',
            table='train',
        ),
    ]
