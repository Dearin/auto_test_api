
from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^cases/', HandleCasesByModule.as_view()),
    url(r'^tasks/', HandleTasksManage.as_view()),
    url(r'^taskDetail/', HandleTaskDetail.as_view())
]
