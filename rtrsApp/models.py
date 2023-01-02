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
    def __str__(self):
        full = self.first_name+" "+self.last_name
        return full
    class Meta:
        db_table = "r_user"


class Train(models.Model):
    train_id = models.IntegerField()
    name = models.CharField(max_length=50, null=False)
    total_seat_snigdha = models.IntegerField()
    total_seat_schair = models.IntegerField()
    total_seat_shovan = models.IntegerField()
    def __str__(self):
        return self.name
    class Meta:
        db_table = "train"


class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    amount = models.IntegerField()
    date = models.DateField()
    def __str__(self):
        details = ("Id ", self.payment_id, " amount ", self.amount)
        return str(details)
    
    class Meta:
        db_table = "payment"


class Reservation (models.Model):
    reservation_id = models.IntegerField(primary_key=True)
    date_of_reservation = models.DateField()
    date_of_journey = models.DateTimeField()
    num_of_adults = models.IntegerField( blank=False, null=False)
    num_of_childs = models.IntegerField()
    seat_class = models.CharField(max_length=10, blank=False, null=False)
    from_station = models.CharField(max_length=30, blank=False, null=False)
    to_station = models.CharField(max_length=30, blank=False, null=False)
    user = models.ForeignKey(R_user, on_delete=models.CASCADE,)
    # payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    def __str__(self):
        details = "Id ",self.reservation_id," From ", self.from_station, " To ", self.to_station
        return str(details)
    
    class Meta:
        db_table = "Reservation"

class booked_seat(models.Model):
    train = models.ForeignKey(Train, on_delete=models.CASCADE)
    seat_no = models.IntegerField()
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    date_of_journey = models.DateTimeField()
    seat_class = models.CharField(max_length=50)
    # def __str__(self):
    #     details = ("seat no ",self.seat_no+ " of ", self.train, " at " ,self.date_of_journey)
    #     return str(details)
    
    class Meta:
        unique_together = (("train", "seat_no", "reservation"))
        db_table = "booked_seat"
        


class Station(models.Model):
    station_id = models.IntegerField()
    name = models.CharField(max_length=20, null=False)
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = "station"


class Train_Timetable(models.Model):
    train = models.ForeignKey(Train, on_delete=models.CASCADE)
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    departure_time = models.CharField(max_length=20)
    direction = models.CharField(max_length=20,default = 'FROM')
    def __str__(self):
        details  = self.train," at " ,self.station
        return str(details)
    
    class Meta:
        unique_together = (("train", "station", "direction"),)
        db_table = "Train_timetable"


class Cost(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    to_station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='to_station_id')
    cost = models.IntegerField()
    def __str__(self):
        details = (self.station," to ",self.to_station)
        return str(details)
    class Meta:
        db_table = "cost"


class Mobile_Banking(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    account_no = models.CharField(max_length=50)
    verification_code = models.IntegerField()
    pin = models.IntegerField()
    # def __str__(self):
    #     return self.payment

    class Meta:
        db_table = "Mobile_Banking"


class Card(models.Model):
    payment_id = models.ForeignKey(Payment, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    card_no = models.CharField(max_length=50)
    expiration_date = models.DateField()
    cvv = models.CharField(max_length=50)
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = "Card"

class Nexuspay(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    card_no = models.CharField(max_length=50)
    pin = models.IntegerField()
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = "Nexuspay"
