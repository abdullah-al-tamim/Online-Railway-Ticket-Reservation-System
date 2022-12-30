from django.db import models

# Create your models here.


class R_user(models.Model):
    user_id = models.AutoField(primary_key=True)
    password = models.CharField(max_length=300, blank=False, null=False)
    first_name = models.CharField(max_length=50, blank=False, null=False)
    last_name = models.CharField(max_length=50, blank=False, null=False)
    dob = models.DateField()
    contact_no = models.CharField(max_length=15)
    gender = models.CharField(max_length=10, blank=False, null=False)
    email_add = models.EmailField(max_length=100)
    nid_no = models.CharField(max_length=50, blank=False, null=False)
    house_no = models.CharField(max_length=15)
    road_no = models.CharField(max_length=15)
    zip_code = models.CharField(max_length=15)
    city = models.CharField(max_length=50)

    class Meta:
        db_table = "r_user"


class Train(models.Model):
    train_id = models.IntegerField()
    name = models.CharField(max_length=50, null=False)
    total_seat_snigdha = models.IntegerField()
    total_seat_schair = models.IntegerField()
    total_seat_shovan = models.IntegerField()
    class Meta:
        db_table = "train"


class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    amount = models.IntegerField()
    date = models.DateField()
    class Meta:
        db_table = "payment"


class Reservation (models.Model):
    reservation_id = models.AutoField(primary_key=True)
    date_of_reservation = models.DateField()
    date_of_journey = models.DateTimeField()
    num_of_adults = models.IntegerField( blank=False, null=False)
    num_of_childs = models.IntegerField()
    seat_class = models.CharField(max_length=10, blank=False, null=False)
    from_station = models.CharField(max_length=30, blank=False, null=False)
    to_station = models.CharField(max_length=30, blank=False, null=False)
    user = models.ForeignKey(R_user, on_delete=models.CASCADE,)
    # payment = models.ForeignKey(Payment, on_delete=models.CASCADE)

    class Meta:
        db_table = "Reservation"

class booked_seat(models.Model):
    train = models.ForeignKey(Train, on_delete=models.CASCADE)
    seat_no = models.IntegerField()
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    date_of_journey = models.DateField()
    seat_class = models.CharField(max_length=50)
    class Meta:
        unique_together = (("train", "seat_no", "reservation_id"))
        db_table = "booked_seat"
        


class Station(models.Model):
    station_id = models.IntegerField()
    name = models.CharField(max_length=20, null=False)
    class Meta:
        db_table = "station"


class Train_Timetable(models.Model):
    train = models.ForeignKey(Train, on_delete=models.CASCADE)
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    departure_time = models.CharField(max_length=20)
    direction = models.CharField(max_length=20,default = 'FROM')
    class Meta:
        unique_together = (("train", "station"),)
        db_table = "Train_timetable"


class Cost(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    to_station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='to_station_id')
    cost = models.IntegerField()
    class Meta:
        db_table = "cost"


class Mobile_Banking(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    account_no = models.CharField(max_length=50)
    verification_code = models.IntegerField()
    pin = models.IntegerField()

    class Meta:
        db_table = "Mobile_Banking"


class Card(models.Model):
    payment_id = models.ForeignKey(Payment, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    card_no = models.CharField(max_length=50)
    expiration_date = models.DateField()
    cvv = models.CharField(max_length=50)

    class Meta:
        db_table = "Card"

class Nexuspay(models.Model):
    payment_id = models.ForeignKey(Payment, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    card_no = models.CharField(max_length=50)
    pin = models.IntegerField()

    class Meta:
        db_table = "Nexuspay"
