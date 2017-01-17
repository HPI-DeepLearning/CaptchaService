from django.core.management.base import BaseCommand
from django.conf import settings
from captcha_service.models import CaptchaToken, TextCaptchaToken, ImageCaptchaToken

DATA_PATH = settings.SEED_DATA_PATH
DATASETS = [
(#'icdar_words/Challenge2_Test_Task3_GT.txt',
#'icdar_words/Challenge2_Test_Task3_Images/',
#'text'),

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

    def _create_captcha_token(self, file_path, solution, captcha_type):
        with open(file_path, 'rb') as f:
            image = f.read()
        file_name = file_path.split('/')[-1]
	if captcha_type == "text":
	    token = TextCaptchaToken()
	    token.create(file_name, image, True, solution)
	    token.save()
	elif captcha_type == "image":
	    token = ImageCaptchaToken()
	    token.create(file_name, image, True, solution)
	    token.save()

    def _yield_captcha_data(self):
	for dataset in DATASETS:
	    with open(DATA_PATH + dataset[0], 'r') as f:
		f.readline() # skip header
		for line in f:
		    [file_name, solution] = line.split(';')
		    file_path = DATA_PATH + dataset[1] + file_name
		    solution = solution.strip()
		    yield file_path, solution, dataset[2]

    def handle(self, *args, **options):
        for f_path, solution, captcha_type in self._yield_captcha_data():
            self._create_captcha_token(f_path, solution, captcha_type)
