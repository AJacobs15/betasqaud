from django.conf.urls import patterns, include, url
from People.views import *

urlpatterns = patterns('',
    url(r'^search/', search),
    url(r'^index/', index)
)