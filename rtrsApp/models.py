from django.db import models

# Create your models here.
class R_user(models.Model):
    user_id = models.AutoField(primary_key=True)
    password = models.CharField(max_length=50, blank = False, null = False)
    first_name = models.CharField(max_length=50, blank = False, null = False)
    last_name = models.CharField(max_length=50, blank = False, null = False)
    dob = models.DateField()
    contact_no = models.CharField(max_length=11)
    gender = models.CharField(max_length=10, blank = False, null = False)
    email_add = models.EmailField(max_length=100)
    nid_no = models.CharField(max_length=50, blank = False, null = False)
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
    
class booked_seat(models.Model):
    train_id = models.ForeignKey(Train, on_delete=models.CASCADE)
    seat_no = models.IntegerField()
    reservation_id = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    date_of_journey = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    seat_class = models.CharField()
    class Meta:
        unique_together = (("train_id", "seat_no","reservation_id"))


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


