from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from ipware.ip import get_ip
from .models import CaptchaToken, CaptchaSession, TextCaptchaSession, ImageCaptchaSession
from random import randint
import uuid

@api_view(['GET'])
def request(request):

    remote_ip = get_ip(request)
    session = TextCaptchaSession()
    session, response = session.create(remote_ip)
    session.save()
    return response

@api_view(['GET'])
def get_sessions(request):
    # for debugging purpose
    # CaptchaSession.objects.all().delete()
    sessions = CaptchaSession.objects.all().values()
    print(sessions)
    return Response()

@api_view(['POST'])
def validate(request):
    params = request.POST
    session_key = params.get('session_key', None)
    session = _retrieve_corresponding_session(session_key, request)
    response = session.validate(params)
    return response


@api_view(['POST'])
def renew(request):
    params = request.POST
    session_key = params.get('session_key', None)
    if _any_parameter_unset(session_key):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    session = _retrieve_corresponding_session(session_key, request)
    return session.renew()


def _retrieve_corresponding_session(session_key, request):
    try: 
        session = CaptchaSession.objects.get(pk=session_key)
    except:
        return Response("Session does not exist.", status=status.HTTP_404_NOT_FOUND)
    # assert the remote ip when opening the session and validating them are identical
    # perhaps, remote ip can't be resolved in this case they are evaluated to None - it would still work
    if not get_ip(request) == session.origin:
        return Response("ip when opening the session and ip when validating it are not in agreement.",
                        status=status.HTTP_403_FORBIDDEN)
    
    return session



def _any_parameter_unset(*keys):
        for key in keys:
            if not key:
                return True
        return False 
