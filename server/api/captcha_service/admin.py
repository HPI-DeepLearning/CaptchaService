from django.contrib import admin

from .models import CaptchaToken, TextCaptchaToken, ImageCaptchaToken

# Register your models here.

admin.site.register(CaptchaToken)
admin.site.register(TextCaptchaToken)
admin.site.register(ImageCaptchaToken)