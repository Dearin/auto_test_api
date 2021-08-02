
from django.conf.urls import url

from apps.initialData.views import initialdata

urlpatterns = [
    url(r'^initiladata/', initialdata, name='initialData'),
    ]
