from django.contrib import admin
from rtrsApp.models import R_user , Train, Payment, Reservation , booked_seat, Station, Train_Timetable, Cost, Mobile_Banking, Card, Nexuspay
# Register your models here.
admin.site.register(R_user)
admin.site.register(Train)
admin.site.register(Payment)
admin.site.register(Reservation)
# admin.site.register(booked_seat)
admin.site.register(Station)
admin.site.register(Train_Timetable)
admin.site.register(Cost)
# admin.site.register(Mobile_Banking)
# admin.site.register(Card)
# admin.site.register(Nexuspay)