# -*- coding: utf-8 -*-
# @Time    : 2021/5/15  10:33
# @Author  : charl-z

from django.views.generic import View
from libs.tool import json_response
from django.db.models import Q
from django.core.paginator import Paginator
from testlinkManage.models import TestLinkCaseInfo
from conf.testlink_conf import RUN_TYPE_DICT

class HandleTestLinkView(View, ):
    def get(self, request):
        is_auto = request.GET.get('is_auto')
        belong_to_module = request.GET.get('belong_to_module')
        is_smoke = request.GET.get('is_smoke')
        run_type = request.GET.get('run_type')
        page_size = request.GET.get("page_size")
        current_page = request.GET.get("current_page")

        con = Q()
        if belong_to_module and belong_to_module != 'null':
            belong_to_module_Q = Q()
            belong_to_module_Q.connector = 'OR'
            for i in belong_to_module.split(","):
                belong_to_module_Q.children.append(('belong_to_module', i))
            con.add(belong_to_module_Q, 'AND')

        if run_type and run_type != 'null':
            run_type_Q = Q()
            run_type_Q.connector = 'OR'
            for i in run_type.split(","):
                run_type_Q.children.append(('run_type', RUN_TYPE_DICT[i]))
            con.add(run_type_Q, 'AND')

        if is_smoke and is_smoke != 'null':
            is_smoke = True if is_smoke == 'Yes' else False
            is_smoke_Q = Q(is_smoke=is_smoke)
            con.add(is_smoke_Q, 'AND')

        if is_auto and is_auto != 'null':
            is_auto = True if is_auto == 'Yes' else False
            is_auto_Q = Q(is_auto=is_auto)
            con.add(is_auto_Q, 'AND')

        test_cases = TestLinkCaseInfo.objects.filter(con)
        paginator = Paginator(test_cases, page_size)
        total_case_num = test_cases.count()
        test_cases_page = paginator.page(current_page)

        result = []
        for i in test_cases_page:
            result.append({f.attname: getattr(i, f.attname) for f in i._meta.fields})

        return json_response({
            'code': 200,
            'msg': 'success',
            'data': {
                'count': total_case_num,
                'data': result
            }
        })


class HandleCaseStatistics(View):
    def get(self, request):
        custom_modules = request.GET.get('modules')
        page_size = request.GET.get("page_size")
        current_page = request.GET.get("current_page")
        print(page_size, current_page)

        con = Q()
        if custom_modules and custom_modules != 'null':
            custom_modules_Q = Q()
            custom_modules_Q.connector = 'OR'
            for i in custom_modules.split(","):
                custom_modules_Q.children.append(('belong_to_module', i))
            con.add(custom_modules_Q, 'AND')

        test_module_and_testsuit = TestLinkCaseInfo.objects.filter(con).values(
            "belong_to_module",
            "belong_to_testsuit").distinct("belong_to_module", "belong_to_testsuit")

        paginator = Paginator(test_module_and_testsuit, page_size)
        testsuit_count = test_module_and_testsuit.count()
        testsuit_page = paginator.page(current_page)

        data = []
        count = 0
        for module_and_testsuit in testsuit_page:
            res_dict = dict()
            res = TestLinkCaseInfo.objects.filter(
                belong_to_module=module_and_testsuit['belong_to_module'],
                belong_to_testsuit=module_and_testsuit['belong_to_testsuit'])
            total = res.count()
            is_smoke_num, is_auto_num = 0, 0
            for i in res:
                if i.is_smoke:
                    is_smoke_num += 1
                if i.is_auto:
                    is_auto_num += 1
            count += 1
            res_dict['key'] = count
            res_dict['module_name'] = module_and_testsuit['belong_to_module']
            res_dict['testsuit_name'] = module_and_testsuit['belong_to_testsuit']
            res_dict['case_num'] = total
            res_dict['is_smoke_num'] = is_smoke_num
            res_dict['is_auto_num'] = is_auto_num
            res_dict['not_auto_num'] = total - is_auto_num

            data.append(res_dict)
        return json_response({
            'code': 200,
            'msg': 'success',
            'data': {
                'count': testsuit_count,
                'data': data
            }
        })


class HandleFilter(View):
    def get(self, request):
        belong_to_module = TestLinkCaseInfo.objects.values("belong_to_module").distinct('belong_to_module')
        filter_module = []
        for i in belong_to_module:
            filter_module.append({
                'text': i['belong_to_module'],
                'value': i['belong_to_module']
            })
        return json_response(filter_module)

