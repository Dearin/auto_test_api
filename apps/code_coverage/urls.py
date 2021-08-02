
from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^report/', get_code_coverage_report),
    url(r'^dhcp/', test),
    url(r'^rake_test/', handle_rake_test),
    url(r'^rake_log/', handle_rake_log),


    ]
