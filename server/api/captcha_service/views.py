from django.shortcuts import render
from django.http import HttpResponse

def request(request):
    return render(request, "api_app/request.html", {})

def validate(request):
    return render(request, "api_app/validate.html", {})

def renew(request):
    return render(request, "api_app/renew.html", {})
