# -*- coding: utf-8 -*-
# @Time    : 2020/8/20 12:33
# @Author  : charl-z

from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^handel_remote_host/', HanleRemoteHost.as_view()),

]



