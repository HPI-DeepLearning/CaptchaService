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
from polymorphic.models import PolymorphicModel
import json
from .fields import SeparatedValuesField

class CaptchaToken(PolymorphicModel):
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
	return str(self.id) + ", " + self.captcha_type + ", " + str(self.resolved)

class TextCaptchaToken(CaptchaToken):
    """docstring for TextCaptcha."""

    result = EncryptedCharField(max_length=256)

    def create(self, file_name, file_data, resolved, result=''):
        super(TextCaptchaToken, self).create(file_name, file_data, resolved)
        self.result = result
        self.captcha_type = "text"
        return self

class ImageCaptchaToken(CaptchaToken):

    #The task is a category of pictures and it should be tested if the token belongs to it
    #The result just defines if the token belongs to the given category
    task = models.CharField(max_length=128)
    result = models.BooleanField(default=False)

    def create(self, file_name, file_data, resolved, task, result=False): 
        super(ImageCaptchaToken, self).create(file_name, file_data, resolved)
	self.task = task
        self.result = result
        self.captcha_type = "image"
	return self

class CaptchaSession(PolymorphicModel):
    session_key = models.CharField(primary_key=True, unique=True, max_length=256)

    origin = models.CharField(max_length=128) # ip address

    session_type = models.CharField(max_length=128)

    def create(self, remote_ip, session_type):
	self.session_key = uuid.uuid4()
	self.origin = remote_ip
	self.session_type = session_type

    def _any_parameter_unset(*keys):

	for key in keys:
            if not key:
                return True
        return False


class TextCaptchaSession(CaptchaSession):

    solved_captcha = models.ForeignKey(
        TextCaptchaToken,
        on_delete=models.PROTECT,
        #  limit_choices_to={'resolved': True},
	related_name = 'solved'
    )
    unsolved_captcha = models.ForeignKey(
        TextCaptchaToken,
        on_delete=models.PROTECT,
        #  limit_choices_to={'resolved': False},
	related_name = 'unsolved'
    )
    order = models.BooleanField()# 0 -> solved unsolved 1 -> unsolved solved


    def create(self, remote_ip):
	super(TextCaptchaSession, self).create(remote_ip, 'textsession')
        self.solved_captcha, self.unsolved_captcha = self._get_random_captcha_pair()

        self.order = randint(0,1)
	first_url, second_url = self._adjust_captchas_to_order()

        #create JsonResponse for WebApplication
        response = JsonResponse({'first_url': first_url,
                             'second_url': second_url,
                             'session_key': self.session_key,
	                     'type': 'text'})

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


    def renew(self):
        self.solved_captcha, self.unsolved_captcha = self._get_random_captcha_pair()
	first_url, second_url = self._adjust_captchas_to_order()
	self.save(force_update=True)
	return JsonResponse({'first_url': first_url,
				'second_url': second_url,
				'type' : 'text'})


    @staticmethod
    def _get_random_captcha_pair():
        solved_text_tokens = TextCaptchaToken.objects.filter(resolved=True)
        unsolved_text_tokens = TextCaptchaToken.objects.filter(resolved=False)

	solved_count = solved_text_tokens.count()
	unsolved_count = unsolved_text_tokens.count()

	solved_captcha_index, unsolved_captcha_index = randint(0, solved_count-1), randint(0, unsolved_count-1)

        solved = solved_text_tokens[solved_captcha_index]
        unsolved = unsolved_text_tokens[unsolved_captcha_index]
        return solved, unsolved

    def _adjust_captchas_to_order(self):
	if self.order == 0:
                first_url = self.solved_captcha.file.url
                second_url = self.unsolved_captcha.file.url
        else:
                first_url = self.unsolved_captcha.file.url
                second_url = self.solved_captcha.file.url
	return first_url, second_url

class ImageCaptchaSession(CaptchaSession):

    #order is a list with 0->solved_captcha_token, 1->unsolved_captcha_token
    order = SeparatedValuesField() # customField for saving lists in django

 
    #list with stored captcha_token
    image_token_list = SeparatedValuesField() 
    task = models.TextField(null=True)

    def create(self, remote_ip):
	super(ImageCaptchaSession, self).create(remote_ip, 'imagesession')

	#create order with exactly 4 solved tokens, 0 -> solved, 1 -> unsolved
	self.order = [1] * 9
	i = 0
	while (i < 4):
	    index_solved = randint(0,8)
	    if(self.order[index_solved] == 1):
		self.order[index_solved] = 0
		i += 1


	self.image_token_list = self.get_image_token_list(self.order)
	url_list = []
	for i in range(len(self.image_token_list)):
	    url_list.append(self.image_token_list[i].file.url)

	response = JsonResponse({'url_list' : url_list,
				 'task' : self.task,
				 'session_key': self.session_key,
	                     	 'type': 'image'})
	return self, response

    def validate(self, params):
	result = params.get('result', None)

	if self._any_parameter_unset(self.session_key, result):
	    return Response(status=status.HTTP_400_BAD_REQUEST)

	valid = True
	for index, element in enumerate(self.order):
	    if(element == 0):
		if not (result[index] == self.image_token_list[index].result):
		    valid = False
	
	if (valid == True):
	    for index, element in enumerate(self.order):
		if (element == 1):
		    self.image_token_list[index].add_proposal(result[index])

	return JsonResponse({'valid' : valid})
	

    def renew(self):
	self.task = None
	self.image_token_list = self.get_image_token_list(self.order)

	url_list = []
	for i in range(len(self.image_token_list)): 
	    url_list.append(self.image_token_list[i].file.url)

	self.save(force_update=True)
	return JsonResponse({'url_list' : url_list,
				 'task' : self.task,
	                     	'type': 'image'})

    def get_image_token_list(self, order_list):
	token_list = []
	current_token = models.ForeignKey(
        ImageCaptchaToken,
        on_delete=models.PROTECT,
    )

	image_tokens = ImageCaptchaToken.objects.all()
	count = image_tokens.count()
	for boolean in order_list:
	#TODO limit choices to resolved/unresolved tokens
	    if (boolean == True):
		current_token_index = randint(0,count-1)
		current_token = image_tokens[current_token_index]
		#choose task randomly by first token
		if(self.task == None):
		    self.task = current_token.task
	    else:
		count = ImageCaptchaToken.objects.count()
		current_token_index = randint(0,count-1)
		current_token = image_tokens[current_token_index]
	    token_list.append(current_token)
	return token_list
