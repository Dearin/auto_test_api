from django.http import HttpResponse
from django.shortcuts import render
from .models import ApiCases


# Create your views here.

def moduleCases(request, module_name):
    cases = ApiCases.objects.get()
    return HttpResponse("This is moduleCases %s." % module_name)
