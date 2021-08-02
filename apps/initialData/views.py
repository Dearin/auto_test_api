import json
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.core import serializers
from django.http import JsonResponse
import json


def initialdata(request):
    return JsonResponse("Hello, world. You're at the initialData index.")
