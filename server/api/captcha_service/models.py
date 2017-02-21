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
from random import randint, choice
import uuid
from polymorphic.models import PolymorphicModel
import json
from .fields import SeparatedValuesField
from datetime import datetime
from datetime import timedelta
from django.utils import timezone


class CaptchaToken(PolymorphicModel):
    # Superclass for tokens

    file = models.ImageField(upload_to='static/captchas/')
    # counter object that counts user proposals
    # to this captcha. If captcha is solved None is saved.
    proposals = PickledObjectField()
    resolved = models.BooleanField(default=False)
    captcha_type = models.CharField(max_length=128)
    unsolvable = models.BooleanField(default=False)

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

    def create(self, file_name, file_data, resolved, result='', unsolvable=False):
        super(TextCaptchaToken, self).create(file_name, file_data, resolved)
        self.result = result
        self.captcha_type = "text"
        return self

    # solves token if 3 matching proposals were made
    # marks token as unsolveable if more than 6 resolutions didn't result in
    # solved token
    def try_solve(self):
        # checks if there is a solution for a token based on saved proposals
        proposals = self.proposals
        most_common = proposals.most_common()
        num_proposoals = sum(proposals.values())

        if len(proposals.values()) >= 6:  # more than six different proposals
            self.unsolvable = True
            self.resolved = True
            self.save()
        elif num_proposoals >= 3:
            if most_common[0][1] >= 3:
                self.resolved = True
                self.result = most_common[0][0]
                self.save()


class ImageCaptchaToken(CaptchaToken):

    # The task is a category of pictures and it should be tested if the token belongs to it
    # The result just defines if the token belongs to the given category
    task = models.CharField(max_length=128)
    result = models.BooleanField(default=False)

    def create(self, file_name, file_data, resolved, task, result=False):
        super(ImageCaptchaToken, self).create(file_name, file_data, resolved)
        self.task = task
        if result == 'True':
            self.result = True
        else:
            self.result = False
        self.captcha_type = "image"
        return self

    # solves token if 4 matching proposals were made
    # marks token as unsolveable if more than 6 resolutions didn't result in
    # solved token
    def try_solve(self):
        proposals = self.proposals
        most_common = proposals.most_common()
        num_proposoals = sum(proposals.values())

        if num_proposoals >= 6:
            self.unsolvable = True
            self.resolved = True
            self.save()
        elif num_proposoals >= 4:
            if most_common[0][1] >= 4:
                self.resolved = True
                self.result = most_common[0][0]
                self.save()


class CaptchaSession(PolymorphicModel):
    # superclass for sessions

    session_key = models.CharField(
        primary_key=True, unique=True, max_length=256)

    origin = models.CharField(max_length=128)  # ip address

    session_type = models.CharField(max_length=128)

    session_length = models.DurationField()
    expiration_date = models.DateTimeField()

    is_solved = models.BooleanField()

    def create(self, remote_ip, session_type):
        # basic configuration for captcha sessions
        self.session_key = uuid.uuid4()
        self.origin = remote_ip
        self.session_type = session_type
	print type(timezone.now())
        self.session_length = timedelta(minutes=30)
        self.expiration_date = timezone.now() + self.session_length

        self.is_solved = False

    def _any_parameter_unset(*keys):
        for key in keys:
            if not key:
                return True
        return False

    def expand_session(self):
        self.expiration_date = timezone.now() + self.session_length

    def is_expired(self):
        return timezone.now() > self.expiration_date

    # this method is used to ensure that a user has successfully solved the
    # session (and it is still active)
    def is_valid(self):
        return self.is_solved and not self.is_expired()

    # for debugging purposes
    def __str__(self):
        session_key = str(self.session_key)
        expiration_date = self.expiration_date.isoformat()
        time_until_expiration = str(self.expiration_date - timezone.now())
        is_solved = str(self.is_solved)
        is_valid = str(self.is_valid())
        return "session key: " + session_key + \
            ", expiration date: " + expiration_date + \
            ", time until expiration: " + time_until_expiration + \
            ", is solved: " + is_solved + \
            ", is valid: " + is_valid


class TextCaptchaSession(CaptchaSession):

    solved_captcha = models.ForeignKey(
        TextCaptchaToken,
        on_delete=models.PROTECT,
        limit_choices_to={'resolved': True},
        related_name='solved'
    )
    unsolved_captcha = models.ForeignKey(
        TextCaptchaToken,
        on_delete=models.PROTECT,
        limit_choices_to={'resolved': False},
        related_name='unsolved'
    )
    order = models.BooleanField()  # 0 -> solved unsolved 1 -> unsolved solved

    def create(self, remote_ip):
        super(TextCaptchaSession, self).create(remote_ip, 'textsession')
        self.solved_captcha, self.unsolved_captcha = self._get_random_captcha_pair()

        self.order = randint(0, 1)
        first_url, second_url = self._adjust_captchas_to_order()
        # create JsonResponse for WebApplication

        response = JsonResponse({'first_url': first_url,
                                 'second_url': second_url,
                                 'session_key': self.session_key,
                                 'type': 'text'})
        return self, response

    def validate(self, params):
        # checks if client solution for captcha is correct

        result = params.get('result', None).strip()

        try:
            first_result, second_result = result.split(' ')
        except:
            first_result, second_result = None, None
        if self._any_parameter_unset(self.session_key):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if self._any_parameter_unset(first_result, second_result):
            return JsonResponse({'valid': False})
        # validate input
        if self.order == 0 and self.solved_captcha.result.strip() == first_result.strip() or self.order == 1 and self.solved_captcha.result.strip() == second_result.strip():

            valid = True
            self.is_solved = True
            if self.order == 0:
                self.unsolved_captcha.add_proposal(second_result.strip())
            else:
                self.unsolved_captcha.add_proposal(first_result.strip())

            self.unsolved_captcha.try_solve()

        else:
            valid = False

        # choose new tokens if valid is false to prevent brute force
        if (valid == False):
            self.solved_captcha, self.unsolved_captcha = self._get_random_captcha_pair()
            first_url, second_url = self._adjust_captchas_to_order()
            self.save(force_update=True)
	else:
	    first_url, second_url = self._adjust_captchas_to_order()

	return JsonResponse({'valid': valid,
                             'first_url': first_url,
                             'second_url': second_url,
                             'type': 'text'})

    def renew(self):
        # provides new tokens for a session
        self.expand_session()

        self.solved_captcha, self.unsolved_captcha = self._get_random_captcha_pair()
        first_url, second_url = self._adjust_captchas_to_order()
        self.save(force_update=True)
        return JsonResponse({'first_url': first_url,
                             'second_url': second_url,
                             'type': 'text'})

    @staticmethod
    def _get_random_captcha_pair():
        # get unsolved captcha_token
        text_tokens_unsolved = TextCaptchaToken.objects.all().filter(resolved=False)
        count_unsolved = text_tokens_unsolved.count()
        unsolved_captcha_index = randint(0, count_unsolved - 1)
        unsolved = text_tokens_unsolved[unsolved_captcha_index]
        # get solved captcha_token
        text_tokens_solved = TextCaptchaToken.objects.all().filter(resolved=True)
        count_solved = text_tokens_solved.count()
        solved_captcha_index = randint(0, count_solved - 1)
        solved = text_tokens_solved[solved_captcha_index]
        return solved, unsolved

    def _adjust_captchas_to_order(self):
	# returns iamage urls for one solved and one unsolved CaptchaToken and returns them acoording to the order
        if self.order == 0:
            first_url = self.solved_captcha.file.url
            second_url = self.unsolved_captcha.file.url
        else:
            first_url = self.unsolved_captcha.file.url
            second_url = self.solved_captcha.file.url
        return first_url, second_url


class ImageCaptchaSession(CaptchaSession):

    # order is a list with 1->solved_captcha_token, 0->unsolved_captcha_token
    order = SeparatedValuesField()  # customField for saving lists in django

    # list with stored captcha_token
    image_token_list = SeparatedValuesField()
    # The task is a category of pictures and it should be tested if the tokens
    # of the session belong to it
    task = models.TextField(null=True)

    def create(self, remote_ip):
        super(ImageCaptchaSession, self).create(remote_ip, 'imagesession')

        self.order = self.create_order()
        self.task = self.choose_task()

        self.image_token_list = self.get_image_token_list()

	# create list of image urls to send in response
        url_list = []
        for i in range(len(self.image_token_list)):
            url_list.append(self.image_token_list[i].file.url)
        response = JsonResponse({'url_list': url_list,
                                 'task': self.task,
                                 'session_key': self.session_key,
                                 'type': 'image'})

        return self, response

    def validate(self, params):
        # checks if client solution for captcha is correct

        # number of elements that are saved for each token in the
        # image_token_list
        number_of_elements_per_token = 3

        # transorm result string to bool array
        result_string = params.get('result', None)
        if self._any_parameter_unset(self.session_key, result_string):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        result = result_string.split(",")
        for index, element in enumerate(result):
            if element == '1':
                result[index] = True
            else:
                result[index] = False

        self.image_token_list = self.rebuild_image_token_list(
            number_of_elements_per_token)

        solution_list = self.create_solution_list()

        # validation
        valid = True

        for index, element in enumerate(self.order):
            if(element == '1' and result[index] != solution_list[index]):
                valid = False

        # proposals
        if (valid == True):
            self.is_solved = True
            for index, element in enumerate(self.order):
                if (element == '0'):
                    current_token_pk = self.image_token_list[index][0]
                    current_token = CaptchaToken.objects.get(
                        pk=current_token_pk)
                    current_token.add_proposal(result[index])
                    current_token.try_solve()
	
	if (valid == False):
           # choose new tokens if valid is false to prevent brute force
           self.order = self.create_order()
           self.task = self.choose_task()
           self.image_token_list = self.get_image_token_list()
	   url_list = []
           for i in range(len(self.image_token_list)):
               url_list.append(self.image_token_list[i].file.url)
	else:
	    # create list of recent image urls to send in response when valid is true
	    url_list = []
	    # get image urls by the token id saved in image_token_list
            for index in range(len(self.image_token_list)):
		current_token_pk = self.image_token_list[index][0]
		current_token = ImageCaptchaToken.objects.get(pk=current_token_pk)
		url = current_token.file.url
        	url_list.append(url)
	
        return JsonResponse({'valid': valid,
                             'url_list': url_list,
                             'type': 'image',
                             'task': self.task})

    def renew(self):
        # provides new tokens for a session
        self.expand_session()

        self.order = self.create_order()
        self.task = self.choose_task()
        self.image_token_list = self.get_image_token_list()
        url_list = []
        for i in range(len(self.image_token_list)):
            url_list.append(self.image_token_list[i].file.url)

        self.save(force_update=True)
        return JsonResponse({'url_list': url_list,
                             'task': self.task,
                             'type': 'image'})

    def get_image_token_list(self):
        token_list = []
        current_token = models.ForeignKey(
            ImageCaptchaToken,
            on_delete=models.PROTECT,
        )

        for boolean in self.order:
            if (boolean == 1):
                image_tokens = ImageCaptchaToken.objects.all().filter(
                    resolved=True).filter(task=self.task)
            else:
                image_tokens = ImageCaptchaToken.objects.all().filter(
                    resolved=False).filter(task=self.task)
            # if there are no unsolved tokens use solved tokens
            if not image_tokens:
                image_tokens = ImageCaptchaToken.objects.all().filter(
                    resolved=True).filter(task=self.task)
            count = image_tokens.count()
            current_token_index = randint(0, count - 1)
            current_token = image_tokens[current_token_index]
            token_list.append(current_token)
        return token_list

    @staticmethod
    def create_order():
        # create order with exactly 4 solved tokens, 1 -> solved, 0 -> unsolved
        order_list = [0] * 9
        i = 0
        while (i < 4):
            index_solved = randint(0, 8)
            if(order_list[index_solved] == 0):
                order_list[index_solved] = 1
                i += 1
        return order_list

    @staticmethod
    def choose_task():
        aux = ImageCaptchaToken.objects.all()
        count = aux.count()
        index = randint(0, count - 1)
        return aux[index].task

    def rebuild_image_token_list(self, number_of_elements_per_token):
        # custom field used for storing image_token_list doesnt save correct structure of ImageCaptchaToken
        # e.g. [<ImageCaptchaToken: 1155, image, True>] is saved as [1155, image, True]
        # workaround to rebuild normal structure

        rebuild_image_token_list = []
        auxlist = []
        i = 0
        for element in self.image_token_list:
            auxlist.append(element.strip())
            i += 1
            if (i == number_of_elements_per_token):
                rebuild_image_token_list.append(auxlist)
                auxlist = []
                i = 0
        return rebuild_image_token_list

    def create_solution_list(self):
        # results are not stored in image_token_list, so its necessary to get
        # them from db
        solution_list = []
        for token in self.image_token_list:
            solution_list.append(
                ImageCaptchaToken.objects.get(pk=token[0]).result)
        return solution_list
