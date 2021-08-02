
from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^cases/', HandleCasesByModule.as_view()),
]
