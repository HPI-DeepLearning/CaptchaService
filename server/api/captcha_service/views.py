from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
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
import image_distortion

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
    folder_name = data_folder.name.split(".")[0]
    print task

    #TODO test if its zipfile
    zf = zipfile.ZipFile(data_folder, 'r')
    zf.extractall('tempupload')

    path = 'tempupload/' + folder_name+ '/'
    listing = os.listdir(path)
    txtfile = ''
    for file in listing:
	if file.endswith(".txt"):
	    txtfile = file
    if txtfile == '':
	raise IOError('No solution file found')

    if (solved == "unsolved"):
	for file in listing:
	    im = open(path + file, 'rb')
	    image_data = im.read()
	    if file.endswith(".txt"):
		continue	
	    if (captchatype == 'imagecaptcha'):
#		im = open(path + file, 'rb')
#		image_data = im.read()
		token = ImageCaptchaToken()
	        token.create(file, image_data, 0, task)
	    elif (captchatype == 'textcaptcha'):
		file_path = path + file
#		image_data = image_distortion.processImage(file_path)
		token = TextCaptchaToken()
	        token.create(file, image_data, 0)
	    token.save()
	    im.close()
    elif (solved == "solved"):
	for file_name, solution in _yield_captcha_solutions(path, txtfile):
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
    file_path = 'static/captchas/'
    storage_path = 'tempdownload/'
    if not (os.path.exists(storage_path)):
	    os.makedirs(storage_path)

  
    # create list of tokens, that need to be included in zipfile
    file_name_list = []
    if (resolved == False):
	if (captchatype == 'imagecaptcha'):
	    token_list = ImageCaptchaToken.objects.all().filter(resolved=False).filter(task=requested_task)
        elif (captchatype == 'textcaptcha'):
	    token_list = TextCaptchaToken.objects.all().filter(resolved=False)
    elif (resolved == True):
	if (captchatype == 'imagecaptcha'):
	    token_list = ImageCaptchaToken.objects.all().filter(resolved=True).filter(task=requested_task)
        elif (captchatype == 'textcaptcha'):
	    token_list = TextCaptchaToken.objects.all().filter(resolved=True)

    for token in token_list:
	file_name_list.append(token.file.name)
    _create_zipfile(file_path, file_name_list, resolved, storage_path)
   
    zipf = open(storage_path + 'captchas.zip') 
    response = HttpResponse(zipf, content_type=storage_path+'captchas.zip')
    response['Content-Disposition'] = 'attachment; filename="%s"' % 'captchas.zip'
    shutil.rmtree('tempdownload')
    return response
 
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

def _yield_captcha_solutions(path, txtfile):
    with open(path + txtfile, 'r') as f:
        for line in f:
    	    [file_name, solution] = line.split(';')
	    print(file_name)
	    solution = solution.strip()
	    yield file_name, solution


def _any_parameter_unset(*keys):
        for key in keys:
            if not key:
                return True
        return False

def _create_zipfile(file_path, file_name_list, resolved, storage_path):
    zipf = zipfile.ZipFile(storage_path+'captchas.zip', 'w', zipfile.ZIP_DEFLATED)
    storage_path = 'tempdownload/'
    solutiontxt_name = 'CaptchaSolutions.txt'
    
    if (resolved == True):
	solutiontxt_name = 'CaptchaSolutions.txt'
 	solutiontxt = open(storage_path + solutiontxt_name, 'w')		
    
    for element in file_name_list:
	zipf.write(element, 'captchas/'+os.path.basename(file_path+element)) # second argument defines location of element 
	# create txt with solutions for solved captchas
	if (resolved == True):
	    solution = CaptchaToken.objects.get(file=element).result
	    solutiontxt.write(element + "; " + str(solution) + '\n')
    if (resolved == True):
	solutiontxt.close()
	zipf.write(storage_path + solutiontxt_name, os.path.basename(file_path+solutiontxt_name))
    zipf.close()
    # 
