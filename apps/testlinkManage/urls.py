# -*- coding: utf-8 -*-
# @Time    : 2020/8/20 12:33
# @Author  : charl-z

from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^handle_test_cases/', HandleTestLinkView.as_view()),
    url(r'^handle_cases_statistics/', HandleCaseStatistics.as_view()),
    url(r'^get_filter_info/', HandleFilter.as_view()),

]



