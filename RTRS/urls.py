"""RTRS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from rtrsApp import views as mainViews
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', mainViews.homepage, name='home_page'),
    path('login', mainViews.login, name='login'),
    
    
    path('trains', mainViews.list_trains, name= 'train'),
    path('registration',mainViews.registration,name= 'register'),
    path('seat_selection',mainViews.seatselection,name= 'seat_selection'),
    # path('updateinfo',mainViews.updateinfo,name= 'updateinfo'),
    # path('changepass',mainViews.changepass,name= 'changepass'),
    # path('changemail',mainViews.changemail,name= 'changemail'),
    # path('changenum',mainViews.changenum,name= 'changenum'),
    # path('prev',mainViews.prev,name= 'prev'),
    # path('upcoming',mainViews.upcoming,name= 'upcoming'),
    path('contactus',mainViews.contactus,name= 'contactus'),
    # path('successful',mainViews.successful,name= 'successful'),
    # path('payment_selection',mainViews.payment_selection,name= 'payment_selection'),
    # path('bkash_payment',mainViews.bkash,name= 'bkash_payment'),
    # path('card_payment',mainViews.card,name= 'card_payment'),
    # path('nexus_payment',mainViews.nexus,name= 'nexus_payment'),
    # path('rocket_payment',mainViews.rocket,name= 'rocket_payment'),
    # path('Ticket',mainViews.pdf,name='ticket'),
    path('forget_pass',mainViews.forgetpass,name='forget_pass'),
    path('forget_pass_change',mainViews.forgetchangepass,name='forget_pass_change'),
    # path('demo',mainViews.demo,name='demo'),

    # path('trains', mainViews.list_trains, name='train'),
]
