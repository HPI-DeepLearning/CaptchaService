from django.db import models
from django.core.files.base import ContentFile
from picklefield.fields import PickledObjectField
from encrypted_fields import EncryptedCharField
from collections import Counter
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from ipware.ip import get_ip
from random import randint
import uuid



class CaptchaToken(models.Model):
    file = models.ImageField(upload_to='static/captchas/')
    # counter object that counts user proposals
    # to this captcha. If captcha is solved None is saved.
    proposals = PickledObjectField()
    resolved = models.BooleanField(default=False)
    captcha_type = models.CharField(max_length=128)

    def create(self, file_name, file_data, resolved):
        self.file.save(file_name, ContentFile(file_data))
        self.proposals = Counter()
        self.resolved = resolved

    def add_proposal(self, proposal):
        self.proposals[proposal] += 1
        self.save()

    def __str__(self):
	return str(self.id) + ", " + self.captcha_type

class TextCaptchaToken(CaptchaToken):
    """docstring for TextCaptcha."""

    result = EncryptedCharField(max_length=256)

    def create(self, file_name, file_data, resolved, result=''):
        CaptchaToken.create(self, file_name, file_data, resolved)
        self.result = result
        self.captcha_type = "text"
        return self

class ImageCaptchaToken(CaptchaToken):

    result = EncryptedCharField(max_length=256)

    def create(self, file_name, file_data, resolved, result=''):
        CaptchaToken.create(self, file_name, file_data, resolved)
        self.result = result
        self.captcha_type = "image"
	return self

class CaptchaSession(models.Model):
    session_key = models.CharField(primary_key=True, unique=True, max_length=256)

    origin = models.CharField(max_length=128) # ip address

    session_type = models.CharField(max_length=128)

    def create(self, remote_ip, session_type):
	self.session_key = uuid.uuid4()
	self.origin = remote_ip
	self.session_type = session_type

class TextCaptchaSession(CaptchaSession):

    solved_captcha = models.ForeignKey(
        TextCaptchaToken,
        on_delete=models.PROTECT,
        #  limit_choices_to={'resolved': True},
        related_name='solved'
    )
    unsolved_captcha = models.ForeignKey(
        TextCaptchaToken,
        on_delete=models.PROTECT,
        #  limit_choices_to={'resolved': False},
        related_name='unsolved'
    )
    order = models.BooleanField()# 0 -> solved unsolved 1 -> unsolved solved


    def create(self, remote_ip):
	CaptchaSession.create(self, remote_ip, 'textsession')
        self.solved_captcha, self.unsolved_captcha = self._get_random_captcha_pair()

        self.order = randint(0,1)
	first_url, second_url = self._adjust_captchas_to_order()

        #create JsonResponse for WebApplication
        response = JsonResponse({'first_url': first_url,
                             'second_url': second_url,
                             'session_key': self.session_key,
	                     'type': 'textcaptcha'})

	return self, response


    def validate(self, params):
        result = params.get('result', None).strip()
        try:
            first_result, second_result = result.split(' ')
	except:
	    first_result, second_result = None, None
	if self._any_parameter_unset(self.session_key, first_result, second_result):
	    return Response(status=status.HTTP_400_BAD_REQUEST)
	# validate input
	if self.order == 0 and self.solved_captcha.result.strip() == first_result.strip() or self.order == 1 and self.solved_captcha.result.strip() == second_result.strip():

	   valid = True
	   if self.order == 0:
	       self.unsolved_captcha.add_proposal(second_result.strip())
	   else:
	       self.unsolved_captcha.add_proposal(first_result.strip())

           #delte session TODO Is it better to delete session in view?
	   self.delete()

        else:
           valid = False

	print(valid)

	return JsonResponse({'valid': valid})

# 	for debugging purpose
#	return JsonResponse({'solved_result': self.solved_captcha.result,
#				 'unsolved_result_2': self.unsolved_captcha.result,
#				 'given_result_1': first_result,
#				 'given_result_2': second_result,
#				 'valid': valid})


    def renew(self, params):
        self.solved_captcha, self.unsolved_captcha = self._get_random_captcha_pair()
	first_url, second_url = self._adjust_captchas_to_order()
	self.save(force_update=True)
	return JsonResponse({'first_url': first_url,
				'second_url': second_url})


    @staticmethod
    def _get_random_captcha_pair():
        # TODO: retrieve one solved and one unsolved captcha token
        count = TextCaptchaToken.objects.count()
        first_captcha, second_captcha = randint(1, count), randint(1, count)
        first = TextCaptchaToken.objects.get(pk=first_captcha)
        second = TextCaptchaToken.objects.get(pk=second_captcha)
        return first, second

    def _any_parameter_unset(*keys):

	for key in keys:
            if not key:
                return True
        return False

    def _adjust_captchas_to_order(self):
	if self.order == 0:
                first_url = self.solved_captcha.file.url
                second_url = self.unsolved_captcha.file.url
        else:
                first_url = self.unsolved_captcha.file.url
                second_url = self.solved_captcha.file.url
	return first_url, second_url
