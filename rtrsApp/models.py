from django.db import models

# Create your models here.


class R_user(models.Model):
    user_id = models.AutoField(primary_key=True)
    password = models.CharField(max_length=50, blank=False, null=False)
    first_name = models.CharField(max_length=50, blank=False, null=False)
    last_name = models.CharField(max_length=50, blank=False, null=False)
    dob = models.DateField()
    contact_no = models.CharField(max_length=11)
    gender = models.CharField(max_length=10, blank=False, null=False)
    email_add = models.EmailField(max_length=100)
    nid_no = models.CharField(max_length=50, blank=False, null=False)
    house_no = models.IntegerField()
    road_no = models.IntegerField()
    zip_code = models.IntegerField()
    city = models.CharField(max_length=50)


class Train(models.Model):
    train_id = models.IntegerField()
    name = models.CharField(max_length=50, null=False)
    total_seat_snigdha = models.IntegerField()
    total_seat_schair = models.IntegerField()
    total_seat_shovan = models.IntegerField()
    # class Meta:
    #     db_table = "train"


class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    amount = models.IntegerField()
    date = models.DateField()


class Reservation (models.Model):
    reservation_id = models.AutoField(primary_key=True)
    date_of_reservation = models.DateField()
    date_of_journey = models.DateTimeField()
    num_of_adults = models.IntegerField(max_value=4, blank=False, null=False)
    num_of_childs = models.IntegerField(max_value=3)
    seat_class = models.CharField(max_length=10, blank=False, null=False)
    from_station = models.CharField(max_length=30, blank=False, null=False)
    to_station = models.CharField(max_length=30, blank=False, null=False)
    user_id = models.ForeignKey(R_user, on_delete=models.CASCADE,)
    payment_id = models.ForeignKey(Payment, on_delete=models.CASCADE)


class booked_seat(models.Model):
    train_id = models.ForeignKey(Train, on_delete=models.CASCADE)
    seat_no = models.IntegerField()
    reservation_id = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    date_of_journey = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    seat_class = models.CharField()

    class Meta:
        unique_together = (("train_id", "seat_no", "reservation_id"))


class Station(models.Model):
    station_id = models.IntegerField()
    name = models.CharField(max_length=20, null=False)

    # class Meta:
    #     db_table = "station"


class Train_Timetable:
    train_id = models.ForeignKey(Train, on_delete=models.CASCADE)
    station_id = models.ForeignKey(Station, on_delete=models)
    departure_time = models.DateTimeField()

    class Meta:
        unique_together = (("train_id", "station_id"),)


class Cost(models.Model):
    station_id = models.ForeignKey(Station, on_delete=models.CASCADE)
    to_station_id = models.ForeignKey(Station, on_delete=models.CASCADE)
    cost = models.IntegerField()


class Mobile_Banking(models.Model):
    payment_id = models.ForeignKey(Payment, on_delete=models.CASCADE)
    account_no = models.CharField()
    verification_code = models.IntegerField()
    pin = models.IntegerField()


class Card(models.Model):
    payment_id = models.ForeignKey(Payment, on_delete=models.CASCADE)
    name = models.CharField()
    card_no = models.CharField()
    expiration_date = models.DateField()
    cvv = models.CharField()


class Nexuspay(models.Model):
    payment_id = models.ForeignKey(Payment, on_delete=models.CASCADE)
    name = models.CharField()
    card_no = models.CharField()
    pin = models.IntegerField()
