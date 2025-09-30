from django.shortcuts import render
from django.http import HttpResponse
  
def mainPage(request):
    return HttpResponse("<h2>mainPage</h2>")

def AuthorizationPage(request):
    return HttpResponse("<h2>AuthorizationPage</h2>")

def RegistrationPage(request):
    return HttpResponse("<h2>RegistrationPage</h2>")