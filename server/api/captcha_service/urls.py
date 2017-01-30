from django.conf.urls import url
from django.conf import settings



from . import views

app_name="captcha_service"

urlpatterns = [
    url(r'^request$', views.request, name="request"),
    url(r'^validate$', views.validate, name="validate"),
    url(r'^renew$', views.renew, name="renew"),
    url(r'upload$', views.upload, name="upload"),
]
