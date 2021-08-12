# -*- coding: utf-8 -*-
# @Time    : 2020/8/20 12:33
# @Author  : charl-z

from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^rpm_make/', HandlejenkinsJob.as_view()),
    url(r'^rpm_log/', HandleJobLogs.as_view()),
    url(r'^tar_make/', HandleTarMake.as_view()),
    url(r'^tar_log/', HandleTarLog.as_view()),
    # url(r'^handle_cases_statistics/', HandleCaseStatistics.as_view()),
]



