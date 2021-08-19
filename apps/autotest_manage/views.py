import json
import time

import jsonpath
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from loguru import logger

from libs.tool import json_response
from .models import ApiCases, ApiCreatedtasks


# Create your views here.
def querySetIsExist(querySet):
    items = []
    if querySet.exists():
        for item in querySet.values():
            items.append(item)
        response = {
            'msg': "success",
            'data': items
        }
    else:
        response = {
            'msg': "没有符合条件的数据",
            'data': None
        }
    return response


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


class HandleTasksManage(View):

    def get(self, request):
        '''获取业务信息'''
        task_name = request.GET.get('task_name')
        logger.info('task_name:{}'.format(task_name))
        if task_name is None:
            querySet = ApiCreatedtasks.objects.all()
            response = querySetIsExist(querySet)
        else:
            task_name = str(task_name)
            querySet = ApiCreatedtasks.objects.all().filter(task_name__icontains=f"{task_name}")
            response = querySetIsExist(querySet)
        return json_response(response)

    def handleCases(self, filter_param, module_name):
        '''
        :param filter: 'case_name','case_type'
        :param module_name: which module
        :return:
        '''
        # 获取用例 objects
        dnsList = []
        dhcpList = []
        gslbList = []
        publicList = []
        allList = []

        dnsCases = ApiCases.objects.all().filter(module='DNS')
        publicCases = ApiCases.objects.all().filter(module='PUBLIC')
        dhcpCases = ApiCases.objects.all().filter(module='DHCP')
        gslbCases = ApiCases.objects.all().filter(module='GSLB')

        # 处理数据
        allData = ApiCases.objects.all().values(filter_param)
        for case in allData:
            allList.append(case)

        dnsData = dnsCases.values(filter_param)
        for case in dnsData:
            dnsList.append(case)
            dnsCount = len(dnsList)

        publicData = publicCases.values(filter_param)
        for case in publicData:
            publicList.append(case)
            publicCount = len(publicList)

        dhcpData = dhcpCases.values(filter_param)
        for case in dhcpData:
            dhcpList.append(case)
            dhcpCount = len(dhcpList)

        gslbData = gslbCases.values(filter_param)
        for case in gslbData:
            gslbList.append(case)
            gslbCount = len(gslbList)

        if module_name == 'gslb':
            return gslbList
        elif module_name == 'dns':
            return dnsList
        elif module_name == 'public':
            return publicList
        elif module_name == 'dhcp':
            return dhcpList
        else:
            return allList

    def post(self, request):
        '''
        todo :
        1、后台参数过滤限制
        2、异常处理
        '''
        data = request.body
        data = data.decode('utf-8')
        data = json.loads(data) if data else {}

        # 用例处理
        try:
            task_name = data['task_name']
            testEnv = data['testEnv']
            # 判断测试环境
            ## 自定义环境
            if testEnv == 'customed':
                master_ip1 = data['master_ip1']
                master_ip2 = data['master_ip2']
                master2 = data['master2_ip']
                slave_ip = data['slave_ip']
                version = data['branch']
                bus_branch = version
                basepack_branch = version
                dns_version = 'dns3'
                test_envir = testEnv
                task_type = data['task_type']
                # 若测试类型为开发自测，这统计勾选的模块和用例
                if task_type == 'selftest':
                    module = data['modules']
                    cases = data['cases']
                elif task_type == 'smoke':
                    module = data['modules']
                    cases = '对应模块的 smoke用例'
                else:  # 全量测试
                    module = data['modules']
                    cases = self.handleCases(filter_param='case_en_name', module_name=module)
                receiver = data['receiver']
                zdns_conf_len = data['zdns_conf_len']
                obj = ApiCreatedtasks(task_name=task_name, task_type=task_type, version=version,
                                      bussiness_branch=bus_branch,
                                      basepacket_branch=basepack_branch, module=module, cases=cases,
                                      dns_ver=dns_version,
                                      zdnf_conf_len=zdns_conf_len, email=receiver, master_ip1=master_ip1,
                                      master_ip2=master_ip2,
                                      master2=master2, slave=slave_ip,
                                      )
                obj.save()
        except Exception as e:
            return json_response(error=e)

        response = {
            'id': obj.id,
            'msg': "successfully added!"
        }
        return json_response(response)


class HandleTaskExecute(View):
    """
    处理自动化任务的逻辑：
    1、鉴于不同任务环境配置要要求不一样，所以目前只提供自定义环境测试
        北京：10.1.107.24 api测试环境 python3
        成都：10.2.2.102 api 测试环境 api_test/自动化平台测试环境 autotestapi
    2、用户新建任务后，点击执行，开始执行该自动化任务：
        (1)若任一节点正在测试中，点击运行的时候给出相关提示
        (2)一个测试环境比如设置最多同时 3 个自动化测试进行执行，超过的地方在用户点击执行时进行提示
        (3) Q: 如何判断当前 unittest 有多少用例需要执行，执行失败的有哪些？-- 有关失败重跑和进度展示
        (4) Q: 如何判断当前任务是否结束？ -- 通过 pid 可以判断吗？

    3、最后的发送邮件，如何发送邮件呢？ --  自定义一个邮件服务器吧
    """

    def post(self, request):
        pass

    def get(self, request):
        pass


class HandleTaskDetail(View):

    def get(self, request):
        if request.GET.get('task_id'):
            id = request.GET.get('task_id')
            querySet = ApiCreatedtasks.objects.all().filter(id=f"{id}")
            response = querySetIsExist(querySet)
        else:
            response = {
                'msg': '没有改数据存在'
            }
        return json_response(response)


