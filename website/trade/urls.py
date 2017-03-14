from django.conf.urls import  url  
from website import settings
from . import views

urlpatterns = [ 
    url(r'^$', views.index, name='index'),
     url(r'^suggestions/$', views.suggestions, name='suggestions'),
    ]