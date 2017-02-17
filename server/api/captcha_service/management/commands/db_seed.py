from django.core.management.base import BaseCommand
from django.conf import settings
from captcha_service.models import CaptchaToken, TextCaptchaToken, ImageCaptchaToken

DATA_PATH = settings.SEED_DATA_PATH
DATASETS = [
    ('icdar_words/Challenge2_Test_Task3_GT.txt',
     'icdar_words/Challenge2_Test_Task3_Images/',
     'text'),

    ('platypus/platypus.txt',
     'platypus/',
     'image'),

    ('brontosaurus/brontosaurus.txt',
     'brontosaurus/',
     'image')
]


class Command(BaseCommand):
    args = ''
    help = 'populates the db with given captcha tokens'

    def _create_captcha_token(self, file_path, solution, captcha_type, resolved):
        with open(file_path, 'rb') as f:
            image = f.read()
        file_name = file_path.split('/')[-1]
        if captcha_type == "text":
            token = TextCaptchaToken()
            token.create(file_name, image, resolved, solution)
            token.save()
        elif captcha_type == "image":
            token = ImageCaptchaToken()
            token.create(file_name, image, resolved, solution, True)
            token.save()

    def _yield_captcha_data(self):
        for dataset in DATASETS:
            file_path = DATA_PATH + dataset[0]
            num_lines = sum(1 for line in open(file_path)) - 1
            with open(file_path, 'r') as f:
                f.readline()  # skip header
                for i, line in enumerate(f):
                    [file_name, solution] = line.split(';')
                    file_path = DATA_PATH + dataset[1] + file_name
                    solution = solution.strip()

                    if i < num_lines / 2:
                        resolved = True
                    else:
                        resolved = False

                    yield file_path, solution, dataset[2], resolved

    def handle(self, *args, **options):
        for f_path, solution, captcha_type, resolved in self._yield_captcha_data():
            self._create_captcha_token(
                f_path, solution, captcha_type, resolved)
