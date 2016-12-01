from django.shortcuts import render
from django.http import JsonResponse
from .models import CaptchaToken
from random import randint

def request(request):
    if request.method == 'GET':
        count = CaptchaToken.objects.all().__len__()
        first_captcha, second_captcha = randint(1, count), randint(1, count)
        first_url = CaptchaToken.objects.get(pk=first_captcha).file.url
        second_url = CaptchaToken.objects.get(pk=second_captcha).file.url
        return JsonResponse({'first_url': first_url,
                             'second_url': second_url})

def validate(request):
    return render(request, "api_app/validate.html", {})

def renew(request):
    return render(request, "api_app/renew.html", {})


def get_random_captcha_pair():
    pass
