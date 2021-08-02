from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from libs.tool import json_response
from .models import ApiCases


# Create your views here.

class HandleCasesByModule(View):

    def get(self, request):
        queryset = ApiCases.objects.all()
        return json_response({
            'code': 200,
            'msg': 'success',
            'data': {
                'data': queryset
            }
        })



