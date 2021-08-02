# -*- coding: utf-8 -*-
import random
import sys

import jsonpath

sys.path.append("../")
from api.BaseModule import *

import json
import urllib3
import base64

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class DNSCommon(BaseModule):

    def __init__(self, AUTH=(username, password), HOST_IP=master_ip, HOST_PORT=master_ip, LANG=lang):
        self.HOST_IP = HOST_IP
        self.HOST_PORT = HOST_PORT
        self.AUTH = AUTH
        self.LANG = LANG

    def addSubZone(self, name, owner=[], servers=[], views=[]):
        """
        添加存根区：add sub-zones
        1、添加视图时，默认封装了设备为 dns-node ： local.master
        """
        json_data = {
            "comment": "",
            "is_enable": "yes",
            "name": name,
            "owners": owner,
            "servers": servers,
            "stub_style": "stub",
            "view": views
        }

    def addAcl(self, name, networks_list, time_strategies=[], exclude_time_strategies=[],
               comment="", uuid="uuid", current_user="admin"):
        '''add acl'''
        json_data = {"name": name,
                     "networks": networks_list,
                     "time_strategies": time_strategies,
                     "exclude_time_strategies": exclude_time_strategies,
                     "comment": comment,
                     "uuid": uuid,
                     "current_user": current_user}
        try:
            resp, resp_code = self.post_response(url=acl_url, auth=self.AUTH, data=json.dumps(json_data))
            assert resp_code == 200
            return resp, resp_code
        except Exception as e:
            logger.error(resp)
            return resp, resp_code

    def addTime(self, name):
        '''add timestrategy '''
        json_data = {
            "comment": "",
            "name": name,
            "type": "period",
            "period_type": "week",
            "start_week": "1",  # 从周一 00：00 开始
            "end_week": "0",  # 从周日 00：00 结束
            "start_time": "00:00",
            "end_time": "00:00"}
        try:
            resp, resp_code = self.post_response(url=time_strategies_url, auth=self.AUTH, data=json.dumps(json_data))
            assert resp_code == 200
            return resp, resp_code
        except Exception as e:
            logger.error(resp)
            return resp, resp_code

    def getAcl(self, name, uuid="uuid", current_user="admin"):
        '''get acl'''
        search_attrs = {"name|network": name}
        json_data = {"search_attrs": search_attrs}
        try:
            resp, resp_code = self.get_response(url=acl_url, auth=self.AUTH, data=json.dumps(json_data))
            assert int(resp['total_size']) >= 1
            return resp, resp_code
        except Exception as e:
            logger.error(['get acl failed', 500])
            return 'get acl failed', 500

    def getAllAcl(self):
        '''get all acl'''
        ids = []
        try:
            resp_list, resp_code = self.get_response(url=acl_url, auth=self.AUTH)
            assert resp_code == 200
            resources_list = resp_list["resources"]
            for resource in resources_list:
                ids.append(resource["id"])
            return ids, resp_code
        except Exception as e:
            logger.error(["get acl list error", resp_code])
            return "get acl list error", resp_code

    def editAcl(self, name, networks, exclude_time_strategies=[],
                comment="", uuid="uuid", current_user="admin"):
        '''edit acl'''
        try:
            get_result, get_code = self.getAcl(name=name)
            assert get_code == 200
            time_strategies = get_result['resources'][0]['time_strategies']
            exclude_time_strategies = get_result['resources'][0]['exclude_time_strategies']
            json_data = {"ids": [name],
                         "networks": networks,
                         "time_strategies": time_strategies,
                         "exclude_time_strategies": exclude_time_strategies,
                         "uuid": uuid,
                         "current_user": current_user}
        except Exception as e:
            logger.error(f"acl : {name} not exist")
            return f"acl : {name} not exist"
        try:
            resp, resp_code = self.put_response(url=acl_url, auth=self.AUTH, data=json.dumps(json_data))
            assert resp_code == 200
            return resp, resp_code
        except Exception as e:
            logger.error(resp)
            return resp, resp_code

    def delAcl(self, name_list=[], batchdel=False, current_user="admin", uuid="uuid"):
        '''del acl'''
        ids = []
        unexist_acl = []
        if batchdel:
            # 批量删除
            ids = self.getAllAcl()[0]
        else:
            for name in name_list:
                try:
                    get_result, get_code = self.getAcl(name=name)
                    if get_code == 500:
                        unexist_acl.append(name)
                    else:
                        assert get_code == 200
                        ids.append(get_result['resources'][0]['id'])
                except Exception as e:
                    logger.error(f"{name} invalid not in acl list")
        json_data = {"ids": ids, "current_user": current_user, "uuid": uuid}
        try:
            resp, resp_code = self.delete_response(url=acl_url, auth=self.AUTH, data=json.dumps(json_data))
            resp_msg = f'{unexist_acl} is ignored because they are not exist'
            assert resp_code == 200
            if unexist_acl == []:
                return resp, resp_code
            return resp, resp_code, resp_msg
        except Exception as e:
            logger.error([f'delete acl failed: {name_list} , info: {resp}', resp_code])
            return f'delete acl failed: {name_list} , info: {resp}', resp_code

    def addView(self, name, acls=[]):
        '''
        :param name: 视图名称
        :param acls: 访问控制列表中，对应 acl的名称c'l
        :return:
        '''
        '''add view'''
        json_data = {"name": name,
                     "owners": dns_node,
                     "filter_aaaa": "no",
                     "recursion_enable": "yes",
                     "non_recursive_acls": [],
                     "bind_ips": ["0.0.0.0"],
                     "fail_forwarder": "",
                     "dns64s": [],
                     "need_tsig_key": "no",
                     "acls": acls,
                     "black_acls": [],
                     "filter_aaaa_ips": ["any"],
                     "try_final_after_forward": "no",
                     "limit_ips": [],
                     "current_user": "admin"}
        try:
            resp, resp_code = self.post_response(url=view_url, auth=self.AUTH, data=json.dumps(json_data))
            assert resp_code == 200
            return resp, resp_code
        except Exception as e:
            logger.error(resp)
            return resp, resp_code

    def getView(self, name, uuid="uuid", current_user="admin"):
        '''get view'''
        search_attrs = {"name|comment": name}
        json_data = {"search_attrs": search_attrs}
        try:
            resp, resp_code = self.get_response(url=view_url, auth=self.AUTH, data=json.dumps(json_data))
            assert int(resp['total_size']) >= 1
            return resp, resp_code
        except Exception as e:
            logger.error(['get view failed', 500])
            return 'get view failed', 500

    def getAllView(self):
        '''get all view'''
        ids = []
        try:
            resp_list, resp_code = self.get_response(url=view_url, auth=self.AUTH)
            assert resp_code == 200
            resources_list = resp_list["resources"]
            for resource in resources_list:
                ids.append(resource["id"])
            return ids, resp_code
        except Exception as e:
            logger.error(["get view list error", resp_code])
            return "get view list error", resp_code

    def editView(self, name, acls=[]):
        '''edit view'''
        try:
            get_result, get_code = self.getView(name=name)
            assert get_code == 200
            ids = get_result['resources'][0]['id']
            json_data = {"ids": [ids],
                         "owners": dns_node,
                         "acls": acls,
                         "current_user": "admin"}
        except Exception as e:
            logger.error([f"view : {name} not exist", get_code])
            return f"view : {name} not exist", get_code
        try:
            resp, resp_code = self.put_response(url=view_url, auth=self.AUTH, data=json.dumps(json_data))
            assert resp_code == 200
            return resp, resp_code
        except Exception as e:
            logger.error([e, resp_code])
            return resp, resp_code

    def addStrategy(self, name, view, comment="", dest_addr="", link_landwith="", snmp_community="", snmp_oid="",
                    snmp_port='161',
                    snmp_version="v1", ):
        '''add dispatcher-strategies'''
        strategyurl = base_url + 'dispatcher-strategies'
        json_data = {
            "comment": "",
            "dest_addr": dest_addr,
            "link_bandwidth": link_landwith,
            "name": name,
            "snmp_community": snmp_community,
            "snmp_oid": snmp_oid,
            "snmp_port": "161",
            "snmp_version": snmp_version,
            "view": view
        }
        try:
            resp, resp_code = self.post_response(url=strategyurl, auth=self.AUTH, data=json.dumps(json_data))
            assert resp_code == 200
            return resp, resp_code
        except Exception as e:
            logger.error([e, resp_code])
            return resp, resp_code

    def delStrategy(self):
        ''' 需要 对应strategy 的 id ,需要在数据库中查找21332'''
        pass

    def delView(self, name_list=[], batchdel=False, current_user="admin", uuid="uuid"):
        '''del view'''
        ids = []
        ids_nodef_add = []
        unexist_view = []
        if batchdel:
            # 批量删除
            ids = self.getAllView()[0]
        else:
            for name in name_list:
                try:
                    get_result, get_code = self.getView(name=name)
                    if get_code == 500:
                        unexist_view.append(name)
                    else:
                        assert get_code == 200
                        ids.append(get_result['resources'][0]['id'])
                except Exception as e:
                    logger.error(f"{name} invalid not in view list")
        for id in ids:
            if id != 'default' and id != 'ADD':
                ids_nodef_add.append(id)
        json_data = {"ids": ids_nodef_add, "current_user": current_user, "uuid": uuid}
        try:
            resp, resp_code = self.delete_response(url=view_url, auth=self.AUTH, data=json.dumps(json_data))
            resp_msg = f'{unexist_view} is ignored because they are not exist'
            assert resp_code == 200
            if unexist_view == []:
                return resp, resp_code
            return resp, resp_code, resp_msg
        except Exception as e:
            logger.error([f'delete view failed: {name_list} , info:{resp}', resp_code])
            return f'delete view failed: {name_list} , info:{resp}', resp_code

    def addDomain(self, category_id, domain_names, comment="", is_enable='yes'):
        ''' add domain'''
        # domain_url = base_url + f'domainname-names'
        json_data = {
            'category_id': category_id,
            'comment': comment,
            'domain_names': domain_names,
            'is_enable': is_enable
        }
        try:
            resp, resp_code = self.post_response(url=domain_url, auth=self.AUTH, data=json.dumps(json_data))
            assert resp_code == 200
            return resp, resp_code
        except Exception as e:
            logger.error([resp, resp_code])
            return resp, resp_code

    def getAllDomains(self):
        path = {
            'path': 'root'
        }
        try:
            resp, resp_code = self.get_response(url=domain_url, auth=self.AUTH, params=path)
            assert resp_code == 200
            print(resp)
            return resp, resp_code
        except Exception as e:
            logger.error([resp, resp_code])
            return resp, resp_code

    def queryAllDomainnames(self, current_user='admin', category_id='*', uuid='uuid', page_num=1, page_size="30",
                            sort_col="", sort_ord=""):
        ''' 查找所有的 time-strtegies '''
        # 为啥都要携带这个呢
        url = domain_url + "/%s" % category_id
        json_data = {"uuid": uuid, "current_user": current_user}
        # 全部查找
        params = {"page_num": page_num, "page_size": page_size, "sort_col": sort_col, "sort_ord": sort_ord}
        try:
            resp, resp_code = self.get_response(url=url, auth=self.AUTH, params=params,
                                                data=json.dumps(json_data))
            assert resp_code == 200
            return resp, resp_code
        except Exception as e:
            logger.error([resp, resp_code])
            return resp, resp_code

    def delDomainNameStras(self, current_user='admin', uuid='uuid'):
        '''del all domainnames strategis '''
        ids = []
        resources = self.queryAllDomainnames()[0]['resources']
        for resource in resources:
            ids.append(resource['id'])
        json_data = {"ids": ids, "current_user": current_user, "uuid": uuid}
        if len(ids) == 0:
            logger.info("There is no domainnames to delete")
        else:
            try:
                resp, resp_code = self.delete_response(url=domain_url, auth=self.AUTH, data=json.dumps(json_data))
                assert resp_code == 200
                logger.success("delete all domainnames success")
                return resp, resp_code
            except Exception as e:
                logger.error([f'delete domainname failed, info: {resp}', resp_code])
                return f'delete acl failed , info: {resp}', resp_code

    def queryAllTimeObjs(self, current_user='admin', uuid='uuid', page_num=1, page_size="30",
                         sort_col="", sort_ord=""):
        ''' 查找所有的 time-strtegies '''
        # 为啥都要携带这个呢
        json_data = {"uuid": uuid, "current_user": current_user}
        # 全部查找
        params = {"page_num": page_num, "page_size": page_size, "sort_col": sort_col, "sort_ord": sort_ord}
        try:
            resp, resp_code = self.get_response(url=time_strategies_url, auth=self.AUTH, params=params,
                                                data=json.dumps(json_data))
            assert resp_code == 200
            return resp, resp_code
        except Exception as e:
            logger.error([resp, resp_code])
            return resp, resp_code

    def delAllTimeStra(self, current_user='admin', uuid='uuid'):
        '''del all time-strategis '''
        ids = []
        resources = self.queryAllTimeObjs()[0]['resources']
        for resource in resources:
            ids.append(resource['id'])
        json_data = {"ids": ids, "current_user": current_user, "uuid": uuid}
        if len(ids) >= 1:
            try:
                resp, resp_code = self.delete_response(url=time_strategies_url, auth=self.AUTH,
                                                       data=json.dumps(json_data))
                assert resp_code == 200
                logger.success("delete all time-strategies success")
                return resp, resp_code
            except Exception as e:
                logger.error([f'delete time-strategies failed, info: {resp}', resp_code])
                return f'delete acl failed , info: {resp}', resp_code
        else:
            logger.info('there is no time-strategies to delete')

    def addSmartLoad(self, acls, view, time_strategies=[]):
        """ add smart-loads ,have to add view and acl before"""
        json_data = {
            "comment": "",
            "smart_loads": [
                {
                    "zone_names": ["游戏网站"],
                    "acls": acls,
                    "exclude_time_strategies": [],
                    "time_strategies": time_strategies,
                    "view": view
                }
            ]
        }
        try:
            resp, resp_code = self.post_response(url=smart_loads_url, auth=self.AUTH, data=json.dumps(json_data))
            assert resp_code == 200
            return resp, resp_code
        except Exception as e:
            logger.error([resp, resp_code])
            return resp, resp_code

    def queryAllSmartloads(self, current_user='admin', category_id='*', uuid='uuid', page_num=1, page_size="30",
                           sort_col="", sort_ord=""):
        json_data = {"uuid": uuid, "current_user": current_user}
        # 全部查找
        params = {"page_num": page_num, "page_size": page_size, "sort_col": sort_col, "sort_ord": sort_ord}
        try:
            resp, resp_code = self.get_response(url=smart_loads_url, auth=self.AUTH, params=params,
                                                data=json.dumps(json_data))
            assert resp_code == 200
            return resp, resp_code
        except Exception as e:
            logger.error([resp, resp_code])
            return resp, resp_code

    def delAllSmartLoads(self, current_user='admin', uuid='uuid'):
        ''' delete all smartloads'''
        resources = self.queryAllSmartloads()[0]['resources']
        ids = []
        for resource in resources:
            ids.append(resource['id'])

        json_data = {
            "uuid": uuid,
            "current_user": current_user,
            "ids": ids
        }
        if len(ids) == 0:
            logger.info("There is no smartloads to delete ")
        else:
            try:
                resp, resp_code = self.delete_response(url=smart_loads_url, auth=self.AUTH,
                                                       data=json.dumps(json_data))
                assert resp_code == 200
                logger.success("delete all smartloads success")
                return resp, resp_code
            except Exception as e:
                logger.error([f'delete smartloads failed, info: {resp}', resp_code])
                return f'delete smartloads failed , info: {resp}', resp_code

    def addDispatcherStra(self, name, snmp_community='public', snmp_port='161', view='default'):
        versions = ['v1', 'v2c']
        version = random.choice(versions)
        link_bandwidth = random.randint(1000, 10000)
        json_data = {
            "comment": "",
            "dest_addr": self.get_random_ip(),
            "link_bandwidth": link_bandwidth,
            "name": name,
            "snmp_community": snmp_community,
            "snmp_oid": ".1.3.6.1.2.1.25.2.2.0",
            "snmp_port": snmp_port,
            "snmp_version": version,
            "view": view
        }
        try:
            resp, resp_code = self.post_response(url=dispatcher_url, auth=self.AUTH, data=json.dumps(json_data))
            assert resp_code == 200
            return resp, resp_code
        except Exception as e:
            logger.error([resp, resp_code])
            return resp, resp_code

    def queryAllDispatcherStrObjs(self, uuid='uuid', current_user='admin', page_num=1, page_size="30",
                                  sort_col="", sort_ord=""):
        ''' 查找所有的 dispatcher-strtegies '''
        # 为啥都要携带这个呢
        json_data = {"uuid": uuid, "current_user": current_user}
        # 全部查找
        params = {"page_num": page_num, "page_size": page_size, "sort_col": sort_col, "sort_ord": sort_ord}
        try:
            resp, resp_code = self.get_response(url=dispatcher_url, auth=self.AUTH, params=params,
                                                data=json.dumps(json_data))
            assert resp_code == 200
            return resp, resp_code
        except Exception as e:
            logger.error([resp, resp_code])
            return resp, resp_code

    def delAllDispatcherStraObjs(self, uuid='uuid', current_user='admin'):
        '''删除所有的 dispacher-strategies'''
        # dispa_ids = jsonpath.jsonpath(obj=dispa_list, expr='$.resources..id') jsonpath报错，异常原因没有找到
        resources = self.queryAllDispatcherStrObjs()[0]["resources"]
        ids = []
        for resource in resources:
            ids.append(resource['id'])
        json_data = {
            "ids": ids, "uuid": uuid, "current_user": current_user
        }
        if len(ids) == 0:
            return logger.info("There is no dispatcher-strategies to delete")
        else:
            try:
                resp, resp_code = self.delete_response(url=dispatcher_url, auth=self.AUTH,
                                                       data=json.dumps(json_data))
                assert resp_code == 200
                logger.success('delete all dispatcher-strategies success')
                return resp, resp_code
            except Exception as e:
                logger.error([resp, resp_code])
                return resp, resp_code

    def addTrigger(self, name, link_mapping, type, dispatch_object=['游戏网站'], response_link='default'):
        '''add trigger'''
        """
        pre-action:
            1、need at least 2 dispatcher-strategies
            2、dispatcher-strategies need to relate with diffrent views
        """
        threhold = ['10', '20', '30', '40', '50', '60', '70', '80', '90']
        json_data = {
            "comments": "",
            "dispatch_object": dispatch_object,
            "is_enable": "yes",
            "link_mapping": link_mapping,
            "name": name,
            "response_link": response_link,
            "threshold": random.choice(threhold),
            "type": type
        }
        if type == 'analysis-link':
            try:
                resp, resp_code = self.post_response(url=trigger_url, auth=self.AUTH, data=json.dumps(json_data))
                assert resp_code == 200
                logger.success(f"add trigger-strategies :[{name}],link-mapping:{link_mapping} success")
                return resp, resp_code
            except Exception as e:
                logger.error([resp, resp_code])
                return resp, resp_code
        else:
            logger.error("等待优化dunamic-load类型的trigger的新增")

    def queryAllTriggers(self, uuid='uuid', current_user="admin", page_num=1, page_size="30", sort_col="", sort_ord=""):
        ''' get all triggers '''
        json_data = {"uuid": uuid, "current_user": current_user}
        # 全部查找
        params = {"page_num": page_num, "page_size": page_size, "sort_col": sort_col, "sort_ord": sort_ord}
        try:
            resp, resp_code = self.get_response(url=trigger_url, auth=self.AUTH, params=params,
                                                data=json.dumps(json_data))
            assert resp_code == 200
            return resp, resp_code
        except Exception as e:
            logger.error([resp, resp_code])
            return resp, resp_code

    def delAllTriggers(self, current_user='admin', uuid='uuid'):
        ''' delete all smartloads'''
        resources = self.queryAllTriggers()[0]['resources']
        ids = []
        for resource in resources:
            ids.append(resource['id'])

        json_data = {
            "uuid": uuid,
            "current_user": current_user,
            "ids": ids
        }
        if len(ids) == 0:
            logger.info("There is no triggers to delete ")
        else:
            try:
                resp, resp_code = self.delete_response(url=trigger_url, auth=self.AUTH,
                                                       data=json.dumps(json_data))
                assert resp_code == 200
                logger.success("delete all triggers success")
                return resp, resp_code
            except Exception as e:
                logger.error([f'delete triggers failed, info: {resp}', resp_code])
                return f'delete triggers failed , info: {resp}', resp_code

    def addZone(self, name, view="default", owners=dns_node, server_type="master", current_user="admin"):
        '''add zone'''
        zone_url = base_url + f'views/{view}/zones'
        json_data = {"name": name,
                     "owners": owners,
                     "server_type": server_type,
                     "default_ttl": 3600,
                     "slaves": [],
                     "ad_controller": [],
                     "current_user": current_user}
        try:
            resp, resp_code = self.post_response(url=zone_url, auth=self.AUTH, data=json.dumps(json_data))
            assert resp_code == 200
            return resp, resp_code
        except Exception as e:
            logger.error([resp, resp_code])
            return resp, resp_code

    def get_zone_param(self, file_name):
        '''zone base64'''
        with open(file_name, 'r', encoding='utf-8') as f:
            content = f.read()
            bytes_url = content.encode("utf-8")
            zone_base64 = base64.b64encode(bytes_url).decode()
        return zone_base64

    def addZoneFile(self, view="default", name=None, zone_base64=None, owners=dns_node):
        '''add zone from file'''
        zone_url = base_url + f'views/{view}/zones'
        if name == "root":
            name = "@"
        json_data = {
            "zone_type": "auth",
            "name": name,
            "owners": owners,
            "server_type": "master",
            "default_ttl": "3600",
            "slaves": [],
            "ad_controller": [],
            "limit_ips": [],
            "zone_content": zone_base64,
            "renewal": "no",
            "dsprimary": "no"}
        try:
            resp, resp_code = self.post_response(url=zone_url, auth=self.AUTH, data=json.dumps(json_data))
            assert resp_code == 200
            return resp, resp_code
        except Exception as e:
            logger.error([resp, resp_code])
            return resp, resp_code

    def getZone(self, name, view="default", current_user="admin"):
        '''get zone'''
        zone_url = base_url + f'views/{view}/zones/{name}'
        json_data = {"current_user": current_user}
        try:
            resp, resp_code = self.get_response(url=zone_url, auth=self.AUTH, data=json.dumps(json_data))
            assert resp_code == 200
            return resp, resp_code
        except Exception as e:
            logger.error('get zone failed', 500)
            return 'get zone failed', 500

    def getAllZone(self, view="default"):
        '''get all zone'''
        zone_url = base_url + f'views/{view}/zones'
        ids = []
        try:
            resp_list, resp_code = self.get_response(url=zone_url, auth=self.AUTH)
            assert resp_code == 200
            resources_list = resp_list["resources"]
            for resource in resources_list:
                ids.append(resource["id"])
            return ids, resp_code
        except Exception as e:
            logger.error([f'get zone list failed:{resp_list}----{e}', resp_code])
            return f'get zone list failed:{resp_list}----{e}', resp_code

    def editZone(self, name, view="default", default_ttl=600, dns_node=dns_node):
        '''edit zone'''
        zone_url = base_url + f'views/{view}/zones'
        try:
            get_result, get_code = self.getZone(name=name)
            assert get_code == 200
            ids = get_result['id']
            json_data = {"ids": [ids],
                         "default_ttl": default_ttl,
                         "owners": dns_node,
                         "current_user": "admin"}
        except Exception as e:
            logger.error([f"zone : {name} not exist", get_code])
            return f"zone : {name} not exist", get_code
        try:
            resp, resp_code = self.put_response(url=zone_url, auth=self.AUTH, data=json.dumps(json_data))
            assert resp_code == 200
            return resp, resp_code
        except Exception as e:
            logger.error([e, resp_code])
            return resp, resp_code

    def delZone(self, name_list=[], view="default", batchdel=False, current_user="admin", uuid="uuid"):
        '''del zone'''
        zone_url = base_url + f'views/{view}/zones'
        ids = []
        ids_nodef_add = []
        unexist_zone = []
        if batchdel:
            # 批量删除
            ids = self.getAllZone(view=view)[0]
        else:
            for name in name_list:
                try:
                    get_result, get_code = self.getZone(name=name, view=view)
                    if get_code == 500:
                        unexist_zone.append(name)
                    else:
                        assert get_code == 200
                        ids.append(get_result['id'])
                except Exception as e:
                    logger.error(f"{name} invalid not in zone list")
        for id in ids:
            if id != 'default' and id != 'ADD':
                ids_nodef_add.append(id)
        json_data = {"ids": ids_nodef_add, "current_user": current_user, "uuid": uuid}
        try:
            resp, resp_code = self.delete_response(url=zone_url, auth=self.AUTH, data=json.dumps(json_data))
            resp_msg = f'{unexist_zone} is ignored because they are not exist'
            assert resp_code == 200
            if unexist_zone == []:
                return resp, resp_code
            return resp, resp_code, resp_msg
        except Exception as e:
            logger.error([f'delete zone failed: {name_list} , info:{e}', resp_code])
            return f'delete zone failed: {name_list} , info:{e}', resp_code

    def addRR(self, zone_name, rname, rdata, rtype="A", ttl="3600", is_enable="yes", view="default",
              owners=dns_node, expire_is_enable="no", server_type="master", current_user="admin"):
        '''add rr'''
        rr_url = base_url + f'views/{view}/zones/{zone_name}/rrs'
        json_data = {"name": rname.rstrip("."),
                     "type": rtype,
                     "ttl": ttl,
                     "rdata": rdata,
                     "is_enable": is_enable,
                     "owners": owners,
                     "expire_is_enable": expire_is_enable,
                     "server_type": server_type,
                     "default_ttl": 3600,
                     "current_user": current_user}
        try:
            resp, resp_code = self.post_response(url=rr_url, auth=self.AUTH, data=json.dumps(json_data))
            assert resp_code == 200
            return resp, resp_code
        except Exception as e:
            logger.error([resp, resp_code])
            return resp, resp_code

    def generate_view_zone_file(self):
        view_list = os.listdir(zone_path)
        # rm all dir or file except default
        for view_name in view_list:
            if view_name != "default":
                if os.path.isdir(f'{zone_path}/{view_name}'):
                    shutil.rmtree(f'{zone_path}/{view_name}')
                else:
                    os.remove(f'{zone_path}/{view_name}')

        for i in range(view_count):
            view_name = f'view_{i}'
            view_dir = f'{zone_path}/{view_name}'
            os.mkdir(view_dir)

            for zonenum in range(random_zone_count):
                zonename = self.get_random_zone()

                zonename = self.get_random_zone()
                zone_filename = f'auth_{zonename}txt'

                with open(f"{zone_path}/{view_name}/{zone_filename}", "w") as e:
                    e.write(f"{zonename} 3600 SOA ns.{zonename} mail.{zonename} 1 28800 3600 604800 1800\n")
                    e.write(f"{zonename} 3600 NS ns.{zonename}\n")
                    e.write(f"ns.{zonename} 3600 A 127.0.0.1\n")
                    for rrnum in range(random_rr_count):
                        generate_rr_result = self.generate_import_rrset(
                            import_rtype_list[random.randint(0, len(import_rtype_list) - 1)])
                        rname = generate_rr_result['name']
                        rtype = generate_rr_result['type']
                        ttl = generate_rr_result['ttl']
                        rdata = generate_rr_result['rdata']
                        e.write(f'{rname}{zonename} {ttl} {rtype} {rdata}\n')

    def generate_import_rrset(self, rtype):
        if rtype.upper() == "A":
            return {"name": self.get_random_zone(), "type": rtype, "ttl": str(random.randint(360, 3600)),
                    "rdata": self.get_random_ip()}
        elif rtype.upper() == "AAAA":
            return {"name": self.get_random_zone(), "type": rtype, "ttl": str(random.randint(360, 3600)),
                    "rdata": self.get_random_ipv6_ip()}
        elif rtype.upper() == "NS":
            return {"name": self.get_random_zone(), "type": rtype, "ttl": str(random.randint(360, 3600)),
                    "rdata": self.get_random_zone()}
        elif rtype.upper() == "CNAME":
            return {"name": self.get_random_zone(), "type": rtype, "ttl": str(random.randint(360, 3600)),
                    "rdata": self.get_random_zone()}
        elif rtype.upper() == "PTR":
            return {"name": self.get_random_zone(), "type": rtype, "ttl": str(random.randint(360, 3600)),
                    "rdata": self.get_random_zone()}
        elif rtype.upper() == "TXT":
            return {"name": self.get_random_zone(), "type": rtype, "ttl": str(random.randint(360, 3600)),
                    "rdata": self.get_random_zone()}
        elif rtype.upper() == "DNAME":
            return {"name": self.get_random_zone(), "type": rtype, "ttl": str(random.randint(360, 3600)),
                    "rdata": self.get_random_zone()}
        elif rtype.upper() == "SPF":
            return {"name": self.get_random_zone(), "type": rtype, "ttl": str(random.randint(360, 3600)),
                    "rdata": self.get_random_zone()}

    def generate_random_rrset(self, rtype):
        if rtype.upper() == "A":
            return {"name": self.get_random_zone(), "type": rtype, "ttl": str(random.randint(360, 3600)),
                    "rdata": [self.get_random_ip()]}
        elif rtype.upper() == "AAAA":
            return {"name": self.get_random_zone(), "type": rtype, "ttl": str(random.randint(360, 3600)),
                    "rdata": [self.get_random_ipv6_ip()]}
        elif rtype.upper() == "MX":
            return {"name": self.get_random_zone(), "type": rtype, "ttl": str(random.randint(360, 3600)),
                    "rdata": f'{str(random.randint(1, 65535))} {self.get_random_zone()}'}
        elif rtype.upper() == "NS":
            return {"name": self.get_random_zone(), "type": rtype, "ttl": str(random.randint(360, 3600)),
                    "rdata": self.get_random_zone()}
        elif rtype.upper() == "CNAME":
            return {"name": self.get_random_zone(), "type": rtype, "ttl": str(random.randint(360, 3600)),
                    "rdata": self.get_random_zone()}
        elif rtype.upper() == "NAPTR":
            return {"name": self.get_random_zone(), "type": rtype, "ttl": str(random.randint(360, 3600)),
                    "rdata": f'101 10 "u" "sip+E2U" "!^.*$!sip:userA@test.zdns.cn!" {self.get_random_zone()}'}
        elif rtype.upper() == "SRV":
            return {"name": self.get_random_zone(), "type": rtype, "ttl": str(random.randint(360, 3600)),
                    "rdata": f'{str(random.randint(1, 65535))} {str(random.randint(1, 65535))} {str(random.randint(1, 65535))} {self.get_random_zone()}'}
        elif rtype.upper() == "PTR":
            return {"name": self.get_random_zone(), "type": rtype, "ttl": str(random.randint(360, 3600)),
                    "rdata": self.get_random_zone()}
        elif rtype.upper() == "TXT":
            return {"name": self.get_random_zone(), "type": rtype, "ttl": str(random.randint(360, 3600)),
                    "rdata": self.get_random_zone()}
        elif rtype.upper() == "DNAME":
            return {"name": self.get_random_zone(), "type": rtype, "ttl": str(random.randint(360, 3600)),
                    "rdata": self.get_random_zone()}
        elif rtype.upper() == "SPF":
            return {"name": self.get_random_zone(), "type": rtype, "ttl": str(random.randint(360, 3600)),
                    "rdata": self.get_random_zone()}
        elif rtype.upper() == "CAA":
            return {"name": self.get_random_zone(), "type": rtype, "ttl": str(random.randint(360, 3600)),
                    "rdata": f'{str(random.randint(1, 10))} issue "{self.get_random_zone()}"'}

    def getRR(self, zone_name, rname, rtype="A", view="default", current_user="admin"):
        '''get rr'''
        rname = rname.rstrip(".")
        name = f'{rname}.{zone_name}.'
        rr_url = base_url + f'views/{view}/zones/{zone_name}/rrs'
        ids = []
        try:
            resp_list, resp_code = self.get_response(url=rr_url, auth=self.AUTH)
            assert resp_code == 200
            resources_list = resp_list["resources"]
            for resource in resources_list:
                if resource['row_id'] > 3 and resource['name'] == name and resource[
                    'type'].lower() == rtype.lower():
                    ids.append(resource["id"])
            if ids == []:
                logger.error([f'get rr failed:{name} {rtype}', 500])
                return f'get rr failed:{name} {rtype}', 500
            return ids, resp_code
        except Exception as e:
            logger.error([f'get rr failed:{name} {rtype}', 500])
            return f'get rr failed:{name} {rtype}', 500

    def getAllRR(self, zone_name, view="default"):
        '''get all rr'''
        rr_url = base_url + f'views/{view}/zones/{zone_name}/rrs'
        ids = []
        try:
            resp_list, resp_code = self.get_response(url=rr_url, auth=self.AUTH)
            assert resp_code == 200
            resources_list = resp_list["resources"]
            for resource in resources_list:
                if resource['row_id'] > 3:
                    ids.append(resource["id"])
            return ids, resp_code
        except Exception as e:
            logger.error([f'get rr list failed:{resp_list}----{e}', resp_code])
            return f'get rr list failed:{resp_list}----{e}', resp_code

    def editRR(self, zone_name, rname, rdata, view="default", rtype="A", ttl="3600", link_ptr="no",
               expire_is_enable="no", expire_time="", expire_style="disable",
               is_enable="yes", uuid="uuid", current_user="admin"):
        '''edit rr'''
        rr_url = base_url + f'views/{view}/zones/{zone_name}/rrs'
        try:
            rr_id, rcode = self.getRR(zone_name, rname, rtype, view, current_user)
            assert rcode == 200
        except:
            logger.error(f'get rr failed: {rname}{zone_name}.')
        if rtype.upper() == "A" or rtype.upper() == "AAAA":
            rdata = rdata[0]
        json_data = {"ids": rr_id,
                     "ttl": ttl,
                     "rdata": rdata,
                     "is_enable": is_enable,
                     "link_ptr": link_ptr,
                     "expire_is_enable": expire_is_enable,
                     "expire_style": expire_style,
                     "expire_time": expire_time,
                     "uuid": uuid,
                     "current_user": current_user}
        try:
            resp, resp_code = self.put_response(url=rr_url, auth=self.AUTH, data=json.dumps(json_data))
            assert resp_code == 200
            return resp, resp_code
        except Exception as e:
            logger.error([resp, resp_code])
            return resp, resp_code

    def delRR(self, zone_name, rname_list, view="default", rtype="A",
              batchdel=False, link_ptr="no", uuid="uuid", current_user="admin"):
        '''del rr'''
        rr_url = base_url + f'views/{view}/zones/{zone_name}/rrs'
        ids = []
        unexist_rr = []
        if batchdel:
            # 批量删除
            ids = self.getAllRR(view=view)[0]
        else:
            for rname in rname_list:
                try:
                    get_result, get_code = self.getRR(zone_name=zone_name, rname=rname, rtype=rtype, view=view,
                                                      current_user=current_user)
                    if get_code == 500:
                        unexist_rr.append(rname)
                    else:
                        assert get_code == 200
                        ids = get_result
                except Exception as e:
                    logger.error(f"{rname} invalid not in rr list")
        json_data = {"ids": ids,
                     "uuid": uuid,
                     "link_ptr": link_ptr,
                     "current_user": current_user}
        try:
            resp, resp_code = self.delete_response(url=rr_url, auth=self.AUTH, data=json.dumps(json_data))
            resp_msg = f'{unexist_rr} is ignored because they are not exist'
            assert resp_code == 200
            if unexist_rr == []:
                return resp, resp_code
            return resp, resp_code, resp_msg
        except Exception as e:
            logger.error([f'delete zone failed: {rname_list} , info:{resp}----{e}', resp_code])
            return f'delete zone failed: {rname_list} , info:{resp}----{e}', resp_code

    def addForwardGroup(self, name, zone_servers_list, comment="", uuid="uuid", current_user="admin"):
        '''add forwardgroup'''
        json_data = {"name": name,
                     "zone_servers": zone_servers_list,
                     "comment": comment,
                     "uuid": uuid,
                     "current_user": current_user}
        try:
            resp, resp_code = self.post_response(url=forwardgroup_url, auth=self.AUTH, data=json.dumps(json_data))
            assert resp_code == 200
            return resp, resp_code
        except Exception as e:
            logger.error([f'add ForwardGroup failed: {name}:{zone_servers_list}, info:{resp}----{e}', resp_code])
            return f'add ForwardGroup failed: {name}:{zone_servers_list}, info:{resp}----{e}', resp_code

    def getForwardGroup(self, name):
        '''get forwardgroup'''
        try:
            search_attrs = {"name|zone_servers|comment": name}
            json_data = {"search_attrs": search_attrs}
            resp, resp_code = self.get_response(url=forwardgroup_url, auth=self.AUTH, data=json.dumps(json_data))
            assert int(resp['total_size']) >= 1
            return resp, resp_code
        except Exception as e:
            logger.error(['get ForwardGroup failed', 500])
            return 'get ForwardGroup failed', 500

    def getAllForwardGroup(self):
        '''add all forwardgroup'''
        ids = []
        try:
            resp_list, resp_code = self.get_response(url=forwardgroup_url, auth=self.AUTH)
            assert resp_code == 200
            resources_list = resp_list["resources"]
            for resource in resources_list:
                ids.append(resource["id"])
            return ids, resp_code
        except Exception as e:
            logger.error([f'getAllForwardGroup list failed:{resp_list}----{e}', resp_code])
            return f'getAllForwardGroup list failed:{resp_list}----{e}', resp_code

    def editForwardGroup(self, name, zone_servers, uuid="uuid", current_user="admin"):
        '''edit forwardgroup'''
        try:
            get_result, get_code = self.getForwardGroup(name)
            assert get_code == 200
            ids = get_result['resources'][0]['id']
            json_data = {"ids": [ids],
                         "zone_servers": zone_servers,
                         "uuid": uuid,
                         "current_user": current_user}
        except Exception as e:
            logger.error([f"ForwardGroup : {name} not exist", get_code])
            return f"ForwardGroup : {name} not exist", get_code
        try:
            resp, resp_code = self.put_response(url=forwardgroup_url, auth=self.AUTH, data=json.dumps(json_data))
            assert resp_code == 200
            return resp, resp_code
        except Exception as e:
            logger.error([f'edit ForwardGroup list failed:{resp}----{e}', resp_code])
            return f'edit ForwardGroup list failed:{resp}----{e}', resp_code

    def delForwardGroup(self, name_list=[], batchdel=False, current_user="admin"):
        '''del forwardgroup'''
        ids = []
        unexist_ForwardGroup = []
        if batchdel:
            # 批量删除
            ids = self.getAllForwardGroup()[0]
        else:
            for name in name_list:
                try:
                    get_result, get_code = self.getForwardGroup(name=name)
                    if get_code == 500:
                        unexist_ForwardGroup.append(name)
                    else:
                        assert get_code == 200
                        ids.append(get_result['resources'][0]['id'])
                except Exception as e:
                    logger.error(f"{name} invalid not in ForwardGroup list")
        json_data = {"ids": ids,
                     "current_user": current_user}
        try:
            resp, resp_code = self.delete_response(url=forwardgroup_url, auth=self.AUTH, data=json.dumps(json_data))
            resp_msg = f'{unexist_ForwardGroup} is ignored because they are not exist'
            assert resp_code == 200
            if unexist_ForwardGroup == []:
                return resp, resp_code
            return resp, resp_code, resp_msg
        except Exception as e:
            logger.error([f'delete ForwardGroup failed: {name_list} , info:{resp}', resp_code])
            return f'delete ForwardGroup failed: {name_list} , info:{resp}', resp_code

    def addForwardZone(self, name, name_type="domain", view=["default"], owners=dns_node, forward_style="First/RTT",
                       servers=[], servers_type="ip", exact_match="no", multi_fetch="no", is_enable="yes",
                       comment="", uuid="uuid", current_user="admin"):
        '''add forwardzone'''
        json_data = {"name": name,
                     "name_type": name_type,
                     "view": view,
                     "owners": owners,
                     "forward_style": forward_style,
                     "servers": servers,
                     "servers_type": servers_type,
                     "exact_match": exact_match,
                     "multi_fetch": multi_fetch,
                     "is_enable": is_enable,
                     "comment": comment,
                     "uuid": uuid,
                     "current_user": current_user}
        if forward_style in ["No"]:
            del json_data["servers"]
            del json_data["servers_type"]
        try:
            resp, resp_code = self.post_response(url=forwardzone_url, auth=self.AUTH, data=json.dumps(json_data))
            assert resp_code == 200
            return resp, resp_code
        except Exception as e:
            logger.error([f'add forwardzone failed: {name}:{name_type}, info:{resp}', resp_code])
            return f'add forwardzone failed: {name}:{name_type}, info:{resp}', resp_code

    def getForwardZone(self, name):
        '''get forwardzone'''
        name_list = []
        try:
            resp, resp_code = self.get_response(url=forwardzone_url, auth=self.AUTH)
            for resource in resp['resources']:
                name_list.append(resource["name"])
            if name not in name_list:
                resp_code = 500
            assert resp_code == 200
            return resource, resp_code
        except Exception as e:
            logger.error([f'forwardzone not found : {name}', resp_code])
            return f'forwardzone not found : {name}', resp_code

    def getAllForwardZone(self):
        '''get all forwardzone'''
        ids = []
        try:
            resp_list, resp_code = self.get_response(url=forwardzone_url, auth=self.AUTH)
            assert resp_code == 200
            resources_list = resp_list["resources"]
            for resource in resources_list:
                ids.append(resource["id"])
            return ids, resp_code
        except Exception as e:
            logger.error(f'getAllForwardZone list failed:{resp_list}----{e}', resp_code)
            return f'getAllForwardZone list failed:{resp_list}----{e}', resp_code

    def delForwardZone(self, name_list=[], batchdel=False, uuid="uuid", current_user="admin"):
        '''del forwardzone'''
        ids = []
        unexist_ForwardZone = []
        if batchdel:
            # 批量删除
            ids = self.getAllForwardZone()[0]
        else:
            for name in name_list:
                try:
                    get_result, get_code = self.getForwardZone(name=name)
                    if get_code == 500:
                        unexist_ForwardZone.append(name)
                    else:
                        assert get_code == 200
                        ids.append(get_result['id'])
                except Exception as e:
                    logger.error(f"{name} invalid not in ForwardZone list")
        json_data = {"ids": ids,
                     "uuid": uuid,
                     "current_user": current_user}
        try:
            resp, resp_code = self.delete_response(url=forwardzone_url, auth=self.AUTH, data=json.dumps(json_data))
            resp_msg = f'{unexist_ForwardZone} is ignored because they are not exist'
            assert resp_code == 200
            if unexist_ForwardZone == []:
                return resp, resp_code
            return resp, resp_code, resp_msg
        except Exception as e:
            logger.error([f'delete Forwardzone failed: {name_list} , info:{resp}', resp_code])
            return f'delete Forwardzone failed: {name_list} , info:{resp}', resp_code

    def getResolutionSuccessRate(self, roll="master"):
        '''get ResolutionSuccessRate'''
        json_data = {"uuid": "uuid", "current_user": "admin"}
        try:
            if roll == "master":
                resp, resp_code = self.get_response(url=resolutionSuccessRate_url, auth=self.AUTH,
                                                    data=json.dumps(json_data))
            elif roll == "monitor1":
                resp, resp_code = self.get_response(url=monitor1_resolutionSuccessRate_url, auth=self.AUTH,
                                                    data=json.dumps(json_data))
            elif roll == "monitor2":
                resp, resp_code = self.get_response(url=monitor2_resolutionSuccessRate_url, auth=self.AUTH,
                                                    data=json.dumps(json_data))
            elif roll == "monitor3":
                resp, resp_code = self.get_response(url=monitor3_resolutionSuccessRate_url, auth=self.AUTH,
                                                    data=json.dumps(json_data))
            assert resp_code == 200
            return int(resp['解析成功率'])
        except Exception as e:
            logger.error([f'get {roll} ResolutionSuccessRate failed', 500])
            return f'get {roll} ResolutionSuccessRate failed'

    def cleanDnsEnv(self):
        '''clean dns env'''
        try:
            logger.info("cleaning dns env")
            # 注意 递归调度-智能负载，需要优先于访问控制模块进行删除
            # self.delAllTriggers()
            # self.delAllDispatcherStraObjs()
            # self.delAllSmartLoads()
            # self.delZone(batchdel=True)
            # self.delView(batchdel=True)
            # self.delAcl(batchdel=True)
            # self.delDomainNameStras()
            # self.delAllTimeStra()
            # self.delForwardZone(batchdel=True)
            # self.delForwardGroup(batchdel=True)
            with open(log_file, 'r+') as file:
                file.truncate(0)
            logger.info("clean dns finished")
        except Exception as e:
            logger.error(f'clean env error!---{e}')


if __name__ == "__main__":
    DNS = DNSCommon()
    DNS.generate_view_zone_file()
