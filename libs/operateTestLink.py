# -*- coding: utf-8 -*-
# @Time    : 2021/5/15  10:33
# @Author  : charl-z

import testlink
import psycopg2
import json
from libs.logger import LogWrapper
from conf.testlink_conf import MODULE_DIC, PROJECT_NAME, KEY, URL, RUN_TYPE_DICT

# 用例ID 用例名称 是否可自动化 是否冒烟 执行类型 自动化ID 用例步骤
log_wrapper = LogWrapper()

class OperateTestLink(object):

    def __init__(self):
        self.tlc = testlink.TestlinkAPIClient(URL, KEY)


    def project_to_id(self) -> dict:
        project_to_id_dict = dict()
        all_project_infos = self.tlc.getProjects()
        for i in all_project_infos:
            project_to_id_dict[i['name']] = i['id']
        return project_to_id_dict

    def _analysis_test_steps(self, steps) -> tuple:
        test_steps = []
        expected_results = []
        for step in steps:
            test_steps.append(step["step_number"]+":" + step["actions"])
            expected_results.append(step["expected_results"])
        return test_steps, expected_results

    def get_test_suite_in_test_suite(self, test_suite_id, test_suite_name) -> dict():
        # 获取
        data = dict()
        test_suits = self.tlc.getTestSuitesForTestSuite(test_suite_id)
        # print(type(test_suits))
        if isinstance(test_suits, dict):
            for i in test_suits.values():
                data[i['name']] = i['id']

        if isinstance(test_suits, list):
            data[test_suite_name] = []

        return data

    def get_cases_in_test_suite(self, project_name, test_suite_id) -> list:
        # 获取用例集下面的所有用例
        test_cases_in_test_suite = self.tlc.getTestCasesForTestSuite(test_suite_id, True, 'full')
        project_id = self.project_to_id()[project_name]
        data = []
        for case in test_cases_in_test_suite:
            case_info_dict = dict()
            external_id = case['external_id']
            case_info_dict['external_id'] = external_id
            case_info_dict['name'] = case['name']
            auto_id = self.tlc.getTestCaseCustomFieldDesignValue(
                external_id,
                int(case['version']), project_id,
                "auto_id", "full")['value']
            is_auto = self.tlc.getTestCaseCustomFieldDesignValue(
                external_id,
                int(case['version']), project_id,
                "enable_auto", "full")['value']
            is_smoke = self.tlc.getTestCaseCustomFieldDesignValue(
                external_id,
                int(case['version']), project_id,
                "smoke", "full")['value']
            run_type = self.tlc.getTestCaseCustomFieldDesignValue(
                external_id,
                int(case['version']), project_id,
                "run_type", "full")['value']
            case_info_dict['auto_id'] = auto_id
            case_info_dict['is_auto'] = True if is_auto == u"是" else False
            case_info_dict['is_smoke'] = True if is_smoke == u"是" else False
            case_info_dict['run_type'] = RUN_TYPE_DICT[run_type]
            case_test_steps, case_expected_result = self._analysis_test_steps(case['steps'])
            case_info_dict['case_test_steps'] = case_test_steps
            case_info_dict['case_expected_result'] = case_expected_result
            data.append(case_info_dict)
        return data


if __name__ == "__main__":
    # try:
    conn = psycopg2.connect(
        database="auto_test",
        user='postgres',
        password='',
        host='127.0.0.1',
        port='5430'
    )
    cur = conn.cursor()
    cur.execute("TRUNCATE test_case_info;")
    operateTestLink = OperateTestLink()
    module_testsuit_dict = dict()

    for key, value in MODULE_DIC.items():
        test_suite_in_test_suite = operateTestLink.get_test_suite_in_test_suite(value, key)
        if test_suite_in_test_suite:
            module_testsuit_dict[key] = test_suite_in_test_suite
        else:
            log_wrapper.info("用例集:{0}，下面可能只存在用例，没有用例集".format(key))
            module_testsuit_dict[key] = {
                "": value
            }
    for module in module_testsuit_dict.keys():
        for testsuit in module_testsuit_dict[module]:
            SQL_TEST_CASE_INFO = "insert into test_case_info(external_id, name, auto_id, is_auto, is_smoke, run_type, belong_to_module, belong_to_testsuit) values"
            SQL_TEST_STEP_INFO = "INSERT INTO test_case_step_info(external_id, case_test_steps, case_expected_result) values"
            for i in operateTestLink.get_cases_in_test_suite(PROJECT_NAME, module_testsuit_dict[module][testsuit]):
                SQL_TEST_CASE_INFO += "('{0}','{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}'),".format(
                    i['external_id'],
                    i['name'].replace("'", ""),
                    i['auto_id'],
                    i['is_auto'],
                    i['is_smoke'],
                    i['run_type'],
                    module,
                    testsuit
                )
                SQL_TEST_STEP_INFO += "('{0}', '{1}', '{2}'),".format(
                    i['external_id'],
                    json.dumps(i['case_test_steps']),
                    json.dumps(i['case_expected_result'])
                )
            SQL_TEST_CASE_INFO = SQL_TEST_CASE_INFO[:-1] + ';'
            SQL_TEST_STEP_INFO = SQL_TEST_STEP_INFO[:-1] + ';'
            # print(SQL_TEST_CASE_INFO)
            # print(SQL_TEST_STEP_INFO)
            log_wrapper.info(SQL_TEST_CASE_INFO)
            cur.execute(SQL_TEST_CASE_INFO)
            # cur.execute(SQL_TEST_STEP_INFO)
            conn.commit()
# except Exception as e:
    #     print("e:", e)
    # finally:
    #     conn.close()


