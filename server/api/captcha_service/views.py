from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.core.management import call_command
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from ipware.ip import get_ip
from .models import CaptchaToken, CaptchaSession, TextCaptchaSession, ImageCaptchaSession, ImageCaptchaToken, TextCaptchaToken
from random import randint, choice
from PIL import Image
import uuid
import zipfile
import shutil
import os

@api_view(['GET'])
def request(request):
    remote_ip = get_ip(request)
    sessions = [ImageCaptchaSession, TextCaptchaSession]
    session = choice(sessions)() # random choice

    session, response = session.create(remote_ip)
    session.save()
    return response


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


@api_view(['POST'])
def upload(request):
    params = request.POST
    captchatype = params.get('captchatype', None)

    solved = params.get('textsolution', None)
    task = params.get('task', None)
    captchafile = request.FILES
    data_folder = captchafile.get('files', None)
    print task

    #TODO test if its zipfile
    zf = zipfile.ZipFile(data_folder, 'r')
    zf.extractall('tempupload')

    path = 'tempupload/captchas/'
    listing = os.listdir(path)

    if (solved == "unsolved"):
	for file in listing:
	    im = open(path + file, 'rb')
	    image_data = im.read()
	    im.close()
	    if (captchatype == 'imagecaptcha'):
		token = ImageCaptchaToken()
	        token.create(file, image_data, 0, task)
	    elif (captchatype == 'textcaptcha'):
		token = TextCaptchaToken()
	        token.create(file, image_data, 0)
	    token.save()
    elif (solved == "solved"):
	for file_name, solution in _yield_captcha_solutions():
	    im = open(path + file_name, 'rb')
	    image_data = im.read()
	    im.close()
	    if (captchatype == 'imagecaptcha'):
		token = ImageCaptchaToken()
		token.create(file_name, image_data, 1, task, solution=='1') #solution=='1' evaluates to bool True
	    elif (captchatype == 'textcaptcha'):
		token = TextCaptchaToken()
		token.create(file_name, image_data, 1, solution)
	    token.save()


    call_command('collectstatic', verbosity=0, interactive=False)
    shutil.rmtree('tempupload')
    return HttpResponseRedirect('/')

@api_view(['GET'])
def download(request):
    params=request.GET
    captchatype = params.get('captchatype', None)
    textsolution = params.get('textsolution', None)
    if (textsolution == 'unsolved'):
	resolved = False
    else:
	resolved = True
    # TODO test if task is working 
    if (captchatype == 'imagecaptcha'): 
	requested_task = params.get('task', None)
 
       
    # create list of tokens, that need to be included in zipfile
    file_name_list = []
    if (resolved == False):
	if (captchatype == 'imagecaptcha'):
	    token_list = ImageCaptchaToken.objects.all().filter(resolved=False).filter(task=requested_task)
        elif (captchatype == 'textcaptcha'):
	    token_list = TextCaptchaToken.objects.all().filter(resolved=False)
    else:
	if (captchatype == 'imagecaptcha'):
	    token_list = ImageCaptchaToken.objects.all().filter(resolved=True).filter(task=requested_task)
        elif (captchatype == 'textcaptcha'):
	    token_list = TextCaptchaToken.objects.all().filter(resolved=True)

    for token in token_list:
	file_name_list.append(token.file.name)
    _create_zipfile('static/captchas/', file_name_list, resolved)
	# fix for Linux zip files read in Windows TODO test
	#for file in zipf.filelist:
	#    file.create_system = 0
    	
    executed = "exec"
    return JsonResponse({'executed': executed})
 
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

def _yield_captcha_solutions():
    with open('tempupload/captchas.txt', 'r') as f:
        for line in f:
    	    [file_name, solution] = line.split(';')
	    solution = solution.strip()
	    yield file_name, solution


def _any_parameter_unset(*keys):
        for key in keys:
            if not key:
                return True
        return False

def _create_zipfile(path, file_name_list, resolved):
    zipf = zipfile.ZipFile('captchas.zip', 'w', zipfile.ZIP_DEFLATED)
    solutiontxt_path = 'tempdownload/'
    solutiontxt_name = 'CaptchaSolutions.txt'
    
    if (resolved == True):
	solutiontxt_path = 'tempdownload/'
	solutiontxt_name = 'CaptchaSolutions.txt'
	if not (os.path.exists(solutiontxt_path)):
	    os.makedirs(solutiontxt_path)
	solutiontxt = open(solutiontxt_path + solutiontxt_name, 'w')		
    
    for element in file_name_list:
	zipf.write(element, 'captchas/'+os.path.basename(path+'captchas/'+element)) # second argument defines location of element 
	# create txt with solutions for solved captchas
	if (resolved == True):
	    solution = CaptchaToken.objects.get(file=element).result
	    solutiontxt.write(element + "; " + str(solution) + '\n')
    solutiontxt.close()
    zipf.write(solutiontxt_path + solutiontxt_name, os.path.basename(path+solutiontxt_name))
    zipf.close()
    # TODO strucure of zip
    shutil.rmtree('tempdownload')

