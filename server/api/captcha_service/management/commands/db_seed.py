from django.core.management.base import BaseCommand
from django.conf import settings
from captcha_service.models import CaptchaToken, TextCaptchaToken

DATA_PATH = settings.SEED_DATA_PATH
CAPTCHA_FILE_1 = 'icdar_words/Challenge2_Test_Task3_GT.txt'
CAPTCHA_PATH_1 = 'icdar_words/Challenge2_Test_Task3_Images/'


class Command(BaseCommand):
    args = ''
    help = 'populates the db with given captcha tokens'

    def _create_captcha_token(self, file_path, solution):
        with open(file_path, 'rb') as f:
            image = f.read()
        file_name = file_path.split('/')[-1]
	token = TextCaptchaToken()
        token.create(file_name, image, True, solution)
        token.save()


    def _yield_captcha_data(self):
        with open(DATA_PATH + CAPTCHA_FILE_1, 'r') as f:
            f.readline() # skip header
            for line in f:
                [file_name, solution] = line.split(';')
                file_path = DATA_PATH + CAPTCHA_PATH_1 + file_name
                solution = solution.strip()
                yield file_path, solution

    def handle(self, *args, **options):
        for f_path, solution in self._yield_captcha_data():
            self._create_captcha_token(f_path, solution)
