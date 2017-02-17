from django.core.management.base import BaseCommand
from captcha_service.models import CaptchaSession
from django.utils import timezone


class Command(BaseCommand):

    def handle(self, *args, **options):
        for session in CaptchaSession.objects.all():
            if session.expiration_date < timezone.now():
                session.delete()
