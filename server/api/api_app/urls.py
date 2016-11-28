from django .conf.urls import url

from . import views

app_name="api_app"
urlpatterns = [
        url(r'^request$', views.request, name="request"),
        url(r'^validate$', views.validate, name="validate"),
        url(r'^renew$', views.renew, name="renew"),
        ]

