from django.contrib import admin
from rtrsApp.models import R_user , Train, Payment, Reservation , booked_seat, Station, Train_Timetable, Cost, Mobile_Banking, Card, Nexuspay

from django.contrib.admin import ModelAdmin, register
# from persons.models import Person


@register(R_user)
class MaterialPersonAdmin(ModelAdmin):
    icon_name = 'person'
@register(Train)
class MaterialPersonAdmin(ModelAdmin):
    icon_name = 'train'
@register(Payment)
class MaterialPersonAdmin(ModelAdmin):
    icon_name = 'payment'
@register(Reservation)
class MaterialPersonAdmin(ModelAdmin):
    icon_name = 'save'
    
@register(Station)
class MaterialPersonAdmin(ModelAdmin):
    icon_name = 'home'
    

@register(Train_Timetable)
class MaterialPersonAdmin(ModelAdmin):
    icon_name = 'query_builder'


@register(Cost)
class MaterialPersonAdmin(ModelAdmin):
    icon_name = 'money'

# Register your models here.


# admin.site.register(R_user)
# admin.site.register(Train)
# admin.site.register(Payment)
# admin.site.register(Reservation)
# admin.site.register(Station)
# admin.site.register(Train_Timetable)
# admin.site.register(Cost)