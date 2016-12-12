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
    # CaptchaSession.objects.all().delete()
    sessions = CaptchaSession.objects.all().values()
    print(sessions)
    return Response()

@api_view(['POST'])
def validate(request):
    # params
    params = request.POST
    session_key = params.get('session_key', None)
    result = params.get('result', None).strip()
    try:
        first_result, second_result = result.split(' ')
    except:
        first_result, second_result = None, None

    if _any_parameter_unset(session_key, first_result, second_result):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    # retrieve coresponding session
    try:
        s = CaptchaSession.objects.get(pk=session_key)
    except:
        return Response("Session does not exist.", status=status.HTTP_404_NOT_FOUND)
    # assert the remote ip when opening the session and validating them are identical
    # perhaps, remote ip can't be resolved in this case they are evaluated to None - it would still work
    if not get_ip(request) == s.origin:
        return Response("ip when opening the session and ip when validating it are not in agreement.",
                        status=status.HTTP_403_FORBIDDEN)
    first_captcha = s.solved_captcha
    second_captcha = s.unsolved_captcha
    # validate input
    if first_result.strip() == first_captcha.result.strip() \
       and second_result.strip() == second_captcha.result.strip():
        valid = True
        # delete session
        s.delete()
    else:
        valid = False
    print(valid)
    return JsonResponse({'actual_result_1': first_captcha.result,
                         'given_result_1': first_result,
                         'actual_result_2': second_captcha.result,
                         'given_result_2': second_result,
                         'valid': valid})

@api_view(['POST'])
def renew(request):
    params = request.POST
    session_key = params.get('session_key', None)
    print(session_key)
    if _any_parameter_unset(session_key):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    s = CaptchaSession.objects.get(session_key=session_key)
    first, second = _get_random_captcha_pair()
    s.update_captchas(first, second)
    return JsonResponse({'first_url': first.file.url,
                         'second_url': second.file.url})



def _get_random_captcha_pair():
    # TODO: retrieve one solved and one unsolved captcha token
    count = CaptchaToken.objects.count()
    first_captcha, second_captcha = randint(1, count), randint(1, count)
    first = CaptchaToken.objects.get(pk=first_captcha)
    second = CaptchaToken.objects.get(pk=second_captcha)
    return first, second

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
