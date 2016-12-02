from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from ipware.ip import get_ip
from .models import CaptchaToken, CaptchaSession
from random import randint
import uuid

@api_view(['GET'])
def request(request):
    if request.method == 'GET':
        first, second = _get_random_captcha_pair()
        f_captcha_id, s_captcha_id = first.id, second.id
        session = _create_session(f_captcha_id, s_captcha_id, request)
        # It's all done now, just send back the file url's
        # and session key to the webapp
        first_url, second_url = first.file.url, second.file.url
        session_id = session.session_key
        session.save()
        return JsonResponse({'first_url': first_url,
                             'second_url': second_url,
                             'session_key': session_id})

@api_view(['GET'])
def get_sessions(request):
    # for debugging purpose
    sessions = CaptchaSession.objects.all().values()
    print(sessions)
    return Response()

@api_view(['POST'])
def validate(request):
    params = request.POST
    session_key = params.get('session_key', None)
    first_result = params.get('first_result', None)
    second_result = params.get('second_result', None)
    if _any_parameter_unset(session_key, first_result, second_result):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    # retrieve coresponding session
    s = CaptchaSession.objects.get(pk=session_key)
    first_captcha = s.solved_captcha_id
    second_captcha = s.unsolved_captcha_id
    # validate input
    if first_result.strip() == first_captcha.result.strip() \
       and second_result.strip() == second_captcha.result.strip():
        valid = True
        # delete session
        s.delete()
    else:
        valid = False
    return JsonResponse({'actual_result_1': first_captcha.result,
                         'given_result_1': first_result,
                         'actual_result_2': second_captcha.result,
                         'given_result_2': second_result,
                         'valid': valid})

@api_view(['POST'])
def renew(request):
    pass  #TODO


def _get_random_captcha_pair():
    # TODO: retrieve one solved and one unsolved captcha token
    count = CaptchaToken.objects.all().__len__()
    first_captcha, second_captcha = randint(1, count), randint(1, count)
    first_url = CaptchaToken.objects.get(pk=first_captcha)
    second_url = CaptchaToken.objects.get(pk=second_captcha)
    return first_url, second_url

def _create_session(first_captcha_id, second_captcha_id, request):
    uid = uuid.uuid4()
    remote_ip = get_ip(request)
    s = CaptchaSession(uid, first_captcha_id,\
                       second_captcha_id, False, remote_ip)
    return s

def _any_parameter_unset(*keys):
    for key in keys:
        if not key:
            return True
    return False
