import json

from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from libs.tool import json_response
from .models import ApiCases


# Create your views here.

class HandleCasesByModule(View):

    def get(self, request):
        # 定义
        dnsCount, dhcpCount, publicCount, gslbCount = 0, 0, 0, 0
        dnsList = []
        dhcpList = []
        gslbList = []
        publicList = []
        # 获取用例 objects
        dnsCases = ApiCases.objects.all().filter(module='DNS')
        publicCases = ApiCases.objects.all().filter(module='PUBLIC')
        dhcpCases = ApiCases.objects.all().filter(module='DHCP')
        gslbCases = ApiCases.objects.all().filter(module='GSLB')

        # 处理数据
        dnsData = dnsCases.values('id', 'case_en_name', 'case_ch_name')
        for case in dnsData:
            dnsList.append(case)
            dnsCount = len(dnsList)

        publicData = publicCases.values('id', 'case_en_name', 'case_ch_name')
        for case in publicData:
            publicList.append(case)
            publicCount = len(publicList)

        dhcpData = dhcpCases.values('id', 'case_en_name', 'case_ch_name')
        for case in dhcpData:
            dhcpList.append(case)
            dhcpCount = len(dhcpList)

        gslbData = gslbCases.values('id', 'case_en_name', 'case_ch_name')
        for case in gslbData:
            gslbList.append(case)
            gslbCount = len(gslbList)

        response = {
            'code': 200,
            'msg': 'success',
            'data': {
                'dns': {
                    'count': dnsCount,
                    'items': dnsList
                },
                'public': {
                    'count': publicCount,
                    'items': publicList
                },
                'dhcp': {
                    'count': dhcpCount,
                    'items': dhcpList
                },
                'gslb': {
                    'count': gslbCount,
                    'items': gslbList
                },
            }
        }
        return json_response(response)
