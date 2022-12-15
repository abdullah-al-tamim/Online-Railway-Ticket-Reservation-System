from django.shortcuts import render, redirect, HttpResponse

# Create your views here.


def homepage(request):
    return render(request, 'search.html', None)


def login(request):
    return render(request, 'login.html', None)


def registration(request):
    return render(request, 'registration.html', None)


def contactus(request):
    return render(request, 'contactus.html', None)
