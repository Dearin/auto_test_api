# -*- coding: utf-8 -*-
import sys

sys.path.append("../")
from api.BaseModule import *

import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class GSLBCommon(BaseModule):
    def __init__(self, AUTH=(username, password), HOST_IP=master_ip, HOST_PORT=master_ip, LANG=lang):
        self.HOST_IP = HOST_IP
        self.HOST_PORT = HOST_PORT
        self.AUTH = AUTH
        self.LANG = LANG

    def addDc(self, name, device, current_user="admin"):
        '''add dc'''
        json_data = {"name": name,
                     "devices": [device],
                     "synserver": device,
                     "current_user": current_user}
        try:
            resp, resp_code = self.post_response(url=dc_url, auth=self.AUTH, data=json.dumps(json_data))
            assert resp_code == 200
            return resp, resp_code
        except Exception as e:
            logger.error(f'add dc {name} failed---{resp}---{resp_code}')
            return resp, resp_code

    def getAllDc(self):
        '''get all dc'''
        ids = []
        try:
            resp_list, resp_code = self.get_response(url=dc_url, auth=self.AUTH)
            assert resp_code == 200
            resources_list = resp_list["resources"]
            for resource in resources_list:
                ids.append(resource["id"])
            return ids, resp_code
        except Exception as e:
            logger.error(["get dc list error", resp_code])
            return "get dc list error", resp_code

    def delAllDc(self, name_list=[], current_user="admin"):
        '''del all dc'''
        if not isinstance(name_list, list):
            name_list = [name_list]
        ids = self.getAllDc()[0]
        json_data = {"ids": ids, "current_user": current_user}
        try:
            resp, resp_code = self.delete_response(url=dc_url, auth=self.AUTH, data=json.dumps(json_data))
            assert resp_code == 200
            return resp, resp_code
        except Exception as e:
            logger.error([f'delete dc failed: {name_list} , info: {resp}', resp_code])
            return f'delete dc failed: {name_list} , info: {resp}', resp_code

    def addHm(self, name, type="icmp", use_4link="yes", message="GET", http_version="HTTP/1.1", current_user="admin"):
        '''add hm_template (type->icmp || tcp || http)'''
        try:
            if type == "icmp":
                json_data = {"name": name,
                             "types": type,
                             "specific_addr": self.get_random_ip(),
                             "use_4link": use_4link,
                             "current_user": current_user}
                if name == "dnsperf_hm_icmp":
                    json_data["specific_addr"] = "127.0.0.1"
                resp, resp_code = self.post_response(url=hm_template_url, auth=self.AUTH, data=json.dumps(json_data))
                assert resp_code == 200
                return resp, resp_code
            elif type == "tcp":
                json_data = {"name": name,
                             "types": type,
                             "specific_addr": self.get_random_ip(),
                             "current_user": current_user}
                resp, resp_code = self.post_response(url=hm_template_url, auth=self.AUTH, data=json.dumps(json_data))
                assert resp_code == 200
                return resp, resp_code
            elif type == "http":
                json_data = {"name": name,
                             "types": type,
                             "message": message,
                             "specific_addr": self.get_random_ip(),
                             "http_version": http_version,
                             "current_user": current_user}
                resp, resp_code = self.post_response(url=hm_template_url, auth=self.AUTH, data=json.dumps(json_data))
                assert resp_code == 200
                return resp, resp_code
        except Exception as e:
            logger.error(f'add hm {name} type {type} failed---{resp}---{resp_code}')
            return resp, resp_code

    def getHm(self, name):
        '''get hm_template'''
        search_attrs = {"name": name}
        json_data = {"search_attrs": search_attrs}
        try:
            resp, resp_code = self.get_response(url=hm_template_url, auth=self.AUTH, data=json.dumps(json_data))
            assert int(resp['total_size']) >= 1
            return resp, resp_code
        except Exception as e:
            logger.error(['get hm_template failed', 500])
            return 'get hm_template failed', 500

    def getAllHm(self, type=None):
        '''get all hm_template'''
        ids = []
        icmp_ids = []
        no_icmp_ids = []
        try:
            resp_list, resp_code = self.get_response(url=hm_template_url, auth=self.AUTH)
            assert resp_code == 200
            resources_list = resp_list["resources"]
            for resource in resources_list:
                ids.append(resource["id"])
                if resource['types'] == "icmp":
                    icmp_ids.append(resource["id"])
            if "dnsperf_hm_icmp" in icmp_ids:
                icmp_ids.remove("dnsperf_hm_icmp")
            if type == "unused":
                used_hms = self.getAllLink()[2]
                unused_hms = []
                for hms_id in ids:
                    if hms_id not in used_hms:
                        unused_hms.append(hms_id)
                for id in unused_hms:
                    if "icmp" not in id:
                        no_icmp_ids.append(id)
                return ids, resp_code, icmp_ids, unused_hms, no_icmp_ids
            else:
                return ids, resp_code, icmp_ids
        except Exception as e:
            logger.error(["get hm_template list error", resp_code])
            return "get hm_template list error", resp_code

    def editHm(self, name):
        '''edit hm_template'''
        try:
            get_result, get_code = self.getHm(name=name)
            assert get_code == 200
            ids = get_result['resources'][0]['id']
            json_data = {"ids": [ids],
                         "check_interval": 155,
                         "timeout": 15,
                         "max_retries": 5,
                         "specific_addr": self.get_random_ip(),
                         "current_user": "admin"}
            if get_result['resources'][0]['types'] == "http":
                json_data['message'] = "GET"
                json_data['http_version'] = "HTTP/1.1"
            elif get_result['resources'][0]['types'] == "icmp":
                json_data['use_4link'] = "yes"
        except Exception as e:
            logger.error([f"hm_template : {name} not exist", get_code])
            return f"hm_template : {name} not exist", get_code
        try:
            resp, resp_code = self.put_response(url=hm_template_url, auth=self.AUTH, data=json.dumps(json_data))
            assert resp_code == 200
            return resp, resp_code
        except Exception as e:
            logger.error([resp, resp_code])
            return resp, resp_code

    def delHm(self, name_list=[], batchdel=False, current_user="admin"):
        '''del hm_template'''
        if not isinstance(name_list, list):
            name_list = [name_list]
        ids = []
        unexist_hm_template = []
        if batchdel:
            # 批量删除
            ids = self.getAllHm()[0]
        else:
            for name in name_list:
                try:
                    get_result, get_code = self.getHm(name=name)
                    if get_code == 500:
                        unexist_hm_template.append(name)
                    else:
                        assert get_code == 200
                        ids.append(get_result['resources'][0]['id'])
                except Exception as e:
                    logger.error(f"{name} invalid not in hm list")
        json_data = {"ids": ids, "current_user": current_user}
        try:
            resp, resp_code = self.delete_response(url=hm_template_url, auth=self.AUTH, data=json.dumps(json_data))
            resp_msg = f'{unexist_hm_template} is ignored because they are not exist'
            assert resp_code == 200
            if unexist_hm_template == []:
                return resp, resp_code
            return resp, resp_code, resp_msg
        except Exception as e:
            logger.error([f'delete hm_template failed: {name_list} , info: {resp}', resp_code])
            return f'delete hm_template failed: {name_list} , info: {resp}', resp_code

    def addLink(self, name, dc, hms, current_user="admin"):
        '''add link'''
        json_data = {"name": name,
                     "dc": dc,
                     "hms": hms,
                     "link_route": self.get_random_ip(),
                     "current_user": current_user}
        try:
            resp, resp_code = self.post_response(url=link_url, auth=self.AUTH, data=json.dumps(json_data))
            assert resp_code == 200
            return resp, resp_code
        except Exception as e:
            logger.error(f'add link {name} failed---{resp}---{resp_code}')
            return resp, resp_code

    def getLink(self, name):
        '''get link'''
        search_attrs = {"name": name}
        json_data = {"search_attrs": search_attrs}
        try:
            resp, resp_code = self.get_response(url=link_url, auth=self.AUTH, data=json.dumps(json_data))
            assert int(resp['total_size']) >= 1
            return resp, resp_code
        except Exception as e:
            logger.error(['get link_url failed', 500])
            return 'get link_url failed', 500

    def getAllLink(self):
        '''get all link'''
        ids = []
        used_hms_id = []
        try:
            resp_list, resp_code = self.get_response(url=link_url, auth=self.AUTH)
            assert resp_code == 200
            resources_list = resp_list["resources"]
            for resource in resources_list:
                ids.append(resource["id"])
                used_hms_id += resource['hms']
            return ids, resp_code, list(set(used_hms_id))
        except Exception as e:
            logger.error(["get link list error", resp_code])
            return "get link list error", resp_code

    def editLink(self, name):
        '''edit Link'''
        try:
            get_result, get_code = self.getLink(name=name)
            assert get_code == 200
            ids = get_result['resources'][0]['id']
            json_data = {"ids": [ids],
                         "dc": random.choice(self.getAllDc()[0]),
                         "hms": random.choice(self.getAllHm(type="icmp")[2]),
                         "link_route": self.get_random_ip()}
        except Exception as e:
            logger.error([f"Link : {name} not exist", get_code])
            return f"Link : {name} not exist", get_code
        try:
            resp, resp_code = self.put_response(url=link_url, auth=self.AUTH, data=json.dumps(json_data))
            assert resp_code == 200
            return resp, resp_code
        except Exception as e:
            logger.error([resp, resp_code])
            return resp, resp_code

    def delLink(self, name_list=[], batchdel=False, current_user="admin"):
        '''del link'''
        if not isinstance(name_list, list):
            name_list = [name_list]
        ids = []
        unexist_link = []
        if batchdel:
            # 批量删除
            ids = self.getAllLink()[0]
        else:
            for name in name_list:
                try:
                    get_result, get_code = self.getLink(name=name)
                    if get_code == 500:
                        unexist_link.append(name)
                    else:
                        assert get_code == 200
                        ids.append(get_result['resources'][0]['id'])
                except Exception as e:
                    logger.error(f"{name} invalid not in link list")
        json_data = {"ids": ids, "current_user": current_user}
        try:
            resp, resp_code = self.delete_response(url=link_url, auth=self.AUTH, data=json.dumps(json_data))
            resp_msg = f'{unexist_link} is ignored because they are not exist'
            assert resp_code == 200
            if unexist_link == []:
                return resp, resp_code
            return resp, resp_code, resp_msg
        except Exception as e:
            logger.error([f'delete link failed: {name_list} , info: {resp}', resp_code])
            return f'delete link failed: {name_list} , info: {resp}', resp_code

    def addGmember(self, name, dc, hms=[], linkid="", current_user="admin"):
        '''add gmember'''
        if len(hms) == 0:
            hms = []
        else:
            if not isinstance(hms, list):
                hms = [hms]
        json_data = {"gmember_name": name,
                     "hms": hms,
                     "ip": self.get_random_ip(),
                     "port": str(random.randint(1, 65535)),
                     "linkid": linkid,
                     "current_user": current_user}
        if name == "gmember_dnsperf_1":
            json_data["ip"] = "1.1.1.1"
        elif name == "gmember_dnsperf_2":
            json_data["ip"] = "2.2.2.2"
        try:
            gmember_url = f"https://{master_ip}:{master_api_port}/dc/{dc}/gmember"
            resp, resp_code = self.post_response(url=gmember_url, auth=self.AUTH, data=json.dumps(json_data))
            assert resp_code == 200
            return resp, resp_code
        except Exception as e:
            logger.error(f'add gmember {name} failed---{resp}---{resp_code}')
            return resp, resp_code

    def getGmember(self, name, dc):
        '''get gmember'''
        search_attrs = {"gmember_name": name}
        json_data = {"search_attrs": search_attrs}
        try:
            gmember_url = f"https://{master_ip}:{master_api_port}/dc/{dc}/gmember"
            resp, resp_code = self.get_response(url=gmember_url, auth=self.AUTH, data=json.dumps(json_data))
            assert int(resp['total_size']) >= 1
            return resp, resp_code
        except Exception as e:
            logger.error(['get gmember failed', 500])
            return 'get gmember failed', 500

    def getAllGmember(self):
        '''get all gmember'''
        ids = []
        used_link_id = []
        new_resources_list = []
        try:
            if len(self.getAllDc()[0]) > 0:
                for dc in self.getAllDc()[0]:
                    gmember_url = f"https://{master_ip}:{master_api_port}/dc/{dc}/gmember"
                    resp_list, resp_code = self.get_response(url=gmember_url, auth=self.AUTH)
                    assert resp_code == 200
                    resources_list = resp_list["resources"]
                    for resource in resources_list:
                        resource["dc_id"] = dc
                        ids.append(resource["id"])
                        used_link_id.append(resource['linkid'])
                        new_resources_list.append(resource)
                return ids, resp_code, list(filter(None, list(set(used_link_id)))), new_resources_list
            else:
                return [], 500, [], []
        except Exception as e:
            logger.error(["get gmember list error", resp_code])
            return "get gmember list error", resp_code

    def delGmember(self, dc="", name_list=[], batchdel=False, current_user="admin"):
        '''del gmember'''
        if not isinstance(name_list, list):
            name_list = [name_list]
        ids = []
        unexist_gmember = []
        if batchdel:
            for gmember in self.getAllGmember()[3]:
                json_data = {"ids": [gmember["id"]], "current_user": current_user}
                dc_id = gmember["dc_id"]
                gmember_url = f"https://{master_ip}:{master_api_port}/dc/{dc_id}/gmember"
                try:
                    resp, resp_code = self.delete_response(url=gmember_url, auth=self.AUTH, data=json.dumps(json_data))
                    assert resp_code == 200
                except Exception as e:
                    logger.error([f'delete gmember failed: {resp}', resp_code])
        #                     return f'delete gmember failed: {resp}', resp_code
        else:
            for name in name_list:
                try:
                    gmember_url = f"https://{master_ip}:{master_api_port}/dc/{dc}/gmember"
                    get_result, get_code = self.getGmember(name=name, dc=dc)
                    if get_code == 500:
                        unexist_gmember.append(name)
                    else:
                        assert get_code == 200
                        ids.append(get_result['resources'][0]['id'])
                except Exception as e:
                    logger.error(f"{name} invalid not in gmember list")
            json_data = {"ids": ids, "current_user": current_user}
            try:
                resp, resp_code = self.delete_response(url=gmember_url, auth=self.AUTH, data=json.dumps(json_data))
                resp_msg = f'{unexist_gmember} is ignored because they are not exist'
                assert resp_code == 200
                if unexist_gmember == []:
                    return resp, resp_code
                return resp, resp_code, resp_msg
            except Exception as e:
                logger.error([f'delete gmember failed: {name_list} , info: {e}', resp_code])
                return f'delete gmember failed: {name_list} , info: {e}', resp_code

    def addSyngroup(self, current_user="admin"):
        '''add syngroup'''
        json_data = {"name": "syngroup_test",
                     "dcs": self.getAllDc()[0],
                     "current_user": current_user}
        try:
            resp, resp_code = self.post_response(url=syngroup_url, auth=self.AUTH, data=json.dumps(json_data))
            assert resp_code == 200
            return resp, resp_code
        except Exception as e:
            logger.error(f'add syngroup syngroup_test failed---{resp}---{resp_code}')
            return resp, resp_code

    def getAllSyngroup(self):
        '''get all syngroup'''
        ids = []
        try:
            resp_list, resp_code = self.get_response(url=syngroup_url, auth=self.AUTH)
            assert resp_code == 200
            resources_list = resp_list["resources"]
            for resource in resources_list:
                ids.append(resource["id"])
            return ids, resp_code
        except Exception as e:
            logger.error(["get syngroup list error", resp_code])
            return "get syngroup list error", resp_code

    def delAllSyngroup(self, current_user="admin"):
        '''del all syngroup'''
        ids = self.getAllSyngroup()[0]
        json_data = {"ids": ids, "current_user": current_user}
        try:
            resp, resp_code = self.delete_response(url=syngroup_url, auth=self.AUTH, data=json.dumps(json_data))
            assert resp_code == 200
            return resp, resp_code
        except Exception as e:
            logger.error([f'delete syngroup failed: {resp}', resp_code])
            return f'delete syngroup failed: {resp}', resp_code

    def addGpool(self, name, hms=[], first_algorithm="sp", current_user="admin", gmember_type="random",
                 user_dc_id=None):
        '''add gpool'''
        if not isinstance(hms, list):
            hms = [hms]
        if len(hms) > 0 and hms != ["dnsperf_hm_icmp"]:
            for i in hms:
                if "icmp" in i:
                    hms.remove(i)
        json_data = {"name": name,
                     "hms": hms,
                     "first_algorithm": first_algorithm,
                     "current_user": current_user}
        if first_algorithm in ["rr", "wrr", "ga"]:
            json_data["fallback_ip"] = self.get_random_ip()
            json_data["fallback_ipv6"] = self.get_random_ipv6_ip()
        if gmember_type != "dnsperf":
            gmember_list = self.getAllGmember()[3]
            if len(gmember_list) > 0:
                gmember = random.choice(gmember_list)
                json_data["gmember_list"] = [
                    {"dc_name": gmember["dc_id"], "gmember_name": gmember["gmember_name"], "ratio": "1"}]
        else:
            json_data["gmember_list"] = [{"dc_name": user_dc_id, "gmember_name": "gmember_dnsperf_1", "ratio": "1"},
                                         {"dc_name": user_dc_id, "gmember_name": "gmember_dnsperf_2", "ratio": "1"}]
        try:
            resp, resp_code = self.post_response(url=gpool_url, auth=self.AUTH, data=json.dumps(json_data))
            assert resp_code == 200
            return resp, resp_code
        except Exception as e:
            logger.error(f'add gpool {name} failed---{resp}---{resp_code}')
            return resp, resp_code

    def getGpool(self, name):
        '''get gpool'''
        search_attrs = {"name": name}
        json_data = {"search_attrs": search_attrs}
        try:
            resp, resp_code = self.get_response(url=gpool_url, auth=self.AUTH, data=json.dumps(json_data))
            assert int(resp['total_size']) >= 1
            return resp, resp_code
        except Exception as e:
            logger.error(['get gpool failed', 500])
            return 'get gpool failed', 500

    def getAllGpool(self):
        '''get all gpool'''
        ids = []
        try:
            resp_list, resp_code = self.get_response(url=gpool_url, auth=self.AUTH)
            assert resp_code == 200
            resources_list = resp_list["resources"]
            for resource in resources_list:
                ids.append(resource["id"])
            return ids, resp_code,
        except Exception as e:
            logger.error(["get gpool list error", resp_code])
            return "get gpool list error", resp_code

    def editGpool(self, name, current_user="admin"):
        '''edit gpool'''
        try:
            get_result, get_code = self.getGpool(name=name)
            assert get_code == 200
            algorithm_list = ["rr", "wrr", "sp", "ga"]
            unused_hms = self.getAllHm(type="unused")[4]
            for hms in unused_hms:
                if "icmp" in str(hms):
                    unused_hms.remove(hms)
            if len(unused_hms) > 0:
                pool_hms = random.choice(unused_hms)
            else:
                pool_hms = []
            first_algorithm = random.choice(algorithm_list)
            ids = get_result['resources'][0]['id']
            json_data = {"ids": [ids],
                         "hms": pool_hms,
                         "first_algorithm": first_algorithm,
                         "current_user": current_user}

            if first_algorithm in ["rr", "wrr", "ga"]:
                json_data["fallback_ip"] = self.get_random_ip()
                json_data["fallback_ipv6"] = self.get_random_ipv6_ip()

            gmember_list = self.getAllGmember()[3]
            if len(gmember_list) > 0:
                gmember = random.choice(gmember_list)
                json_data["gmember_list"] = [
                    {"dc_name": gmember["dc_id"], "gmember_name": gmember["gmember_name"], "ratio": "1"}]
        except Exception as e:
            logger.error([f"gpool : {name} not exist", get_code])
            return f"gpool : {name} not exist", get_code
        try:
            resp, resp_code = self.put_response(url=gpool_url, auth=self.AUTH, data=json.dumps(json_data))
            assert resp_code == 200
            return resp, resp_code
        except Exception as e:
            logger.error([resp, resp_code])
            return resp, resp_code

    def delGpool(self, name_list=[], batchdel=False, current_user="admin"):
        '''del gpool'''
        if not isinstance(name_list, list):
            name_list = [name_list]
        ids = []
        unexist_gpool_template = []
        if batchdel:
            # 批量删除
            ids = self.getAllGpool()[0]
        else:
            for name in name_list:
                try:
                    get_result, get_code = self.getGpool(name=name)
                    if get_code == 500:
                        unexist_gpool_template.append(name)
                    else:
                        assert get_code == 200
                        ids.append(get_result['resources'][0]['id'])
                except Exception as e:
                    logger.error(f"{name} invalid not in gpool list")
        json_data = {"ids": ids, "current_user": current_user}
        try:
            resp, resp_code = self.delete_response(url=gpool_url, auth=self.AUTH, data=json.dumps(json_data))
            resp_msg = f'{unexist_gpool_template} is ignored because they are not exist'
            assert resp_code == 200
            if unexist_gpool_template == []:
                return resp, resp_code
            return resp, resp_code, resp_msg
        except Exception as e:
            logger.error([f'delete gpool failed: {name_list} , info: {resp}', resp_code])
            return f'delete gpool failed: {name_list} , info: {resp}', resp_code

    def addAddZone(self, name, current_user="admin"):
        '''add addZone'''
        synroup_list = self.getAllSyngroup()[0]
        json_data = {"name": name,
                     "syngroup": random.choice(synroup_list),
                     "current_user": current_user}
        try:
            resp, resp_code = self.post_response(url=add_url, auth=self.AUTH, data=json.dumps(json_data))
            assert resp_code == 200
            return resp, resp_code
        except Exception as e:
            logger.error(f'add addzone {name} failed---{resp}---{resp_code}')
            return resp, resp_code

    def getAddZone(self, name):
        '''get addZone'''
        search_attrs = {"name": name}
        json_data = {"search_attrs": search_attrs}
        try:
            resp, resp_code = self.get_response(url=add_url, auth=self.AUTH, data=json.dumps(json_data))
            assert int(resp['total_size']) >= 1
            return resp, resp_code
        except Exception as e:
            logger.error(['get addZone failed', 500])
            return 'get addZone failed', 500

    def getAllAddZone(self):
        '''get all addZone'''
        ids = []
        try:
            resp_list, resp_code = self.get_response(url=add_url, auth=self.AUTH)
            assert resp_code == 200
            resources_list = resp_list["resources"]
            for resource in resources_list:
                ids.append(resource["id"])
            return ids, resp_code,
        except Exception as e:
            logger.error(["get addZone list error", resp_code])
            return "get addZone list error", resp_code

    def delAddZone(self, name_list=[], batchdel=False, current_user="admin"):
        '''del addZone'''
        if not isinstance(name_list, list):
            name_list = [name_list]
        ids = []
        unexist_addzone_template = []
        if batchdel:
            # 批量删除
            ids = self.getAllAddZone()[0]
        else:
            for name in name_list:
                try:
                    get_result, get_code = self.getAddZone(name=name)
                    if get_code == 500:
                        unexist_addzone_template.append(name)
                    else:
                        assert get_code == 200
                        ids.append(get_result['resources'][0]['id'])
                except Exception as e:
                    logger.error(f"{name} invalid not in addZone list")
        json_data = {"ids": ids, "current_user": current_user}
        try:
            resp, resp_code = self.delete_response(url=add_url, auth=self.AUTH, data=json.dumps(json_data))
            resp_msg = f'{unexist_addzone_template} is ignored because they are not exist'
            assert resp_code == 200
            if unexist_addzone_template == []:
                return resp, resp_code
            return resp, resp_code, resp_msg
        except Exception as e:
            logger.error([f'delete addZone failed: {name_list} , info: {resp}', resp_code])
            return f'delete addZone failed: {name_list} , info: {resp}', resp_code

    def addAddRR(self, zone_name, rname, gpool_list=[], gpool_userdef=None, current_user="admin"):
        '''add addRR'''
        algorithm_list = ["rr", "wrr", "sp", "ga"]
        gpools_list = self.getAllGpool()[0]
        if len(gpools_list) > 0:
            gpool_list = [{"gpool_name": random.choice(gpools_list), "ratio": "1"}]
        gmap_url = f'{add_url}/{zone_name}/gmap'
        json_data = {"name": rname,
                     "algorithm": random.choice(algorithm_list),
                     "gpool_list": gpool_list,
                     "current_user": current_user}
        if gpool_userdef:
            json_data["gpool_list"] = [{"gpool_name": gpool_userdef, "ratio": "1"}]
        try:
            resp, resp_code = self.post_response(url=gmap_url, auth=self.AUTH, data=json.dumps(json_data))
            assert resp_code == 200
            return resp, resp_code
        except Exception as e:
            logger.error(f'add addrr {rname}.{zone_name} failed---{resp}---{resp_code}')
            return resp, resp_code

    def getAddRR(self, zone_name, rname):
        '''get addrr'''
        gmap_url = f'{add_url}/{zone_name}/gmap'
        search_attrs = {"name": rname}
        json_data = {"search_attrs": search_attrs}
        try:
            resp, resp_code = self.get_response(url=gmap_url, auth=self.AUTH, data=json.dumps(json_data))
            assert int(resp['total_size']) >= 1
            return resp, resp_code
        except Exception as e:
            logger.error(['get addrr failed', 500])
            return 'get addrr failed', 500

    def getAllAddRR(self, zone_name):
        '''get all addrr'''
        gmap_url = f'{add_url}/{zone_name}/gmap'
        ids = []
        try:
            resp_list, resp_code = self.get_response(url=gmap_url, auth=self.AUTH)
            assert resp_code == 200
            resources_list = resp_list["resources"]
            for resource in resources_list:
                ids.append(resource["id"])
            return ids, resp_code,
        except Exception as e:
            logger.error(["get addrr list error", resp_code])
            return "get addrr list error", resp_code

    def editAddRR(self, zone_name, rname):
        '''edit addrr'''
        try:
            get_result, get_code = self.getAddRR(zone_name, rname)
            assert get_code == 200
            ids = get_result['resources'][0]['id']
            algorithm_list = ["rr", "wrr", "sp", "ga"]
            gpools_list = self.getAllGpool()[0]
            if len(gpools_list) > 0:
                gpool_list = [{"gpool_name": random.choice(gpools_list), "ratio": "1"}]
            else:
                gpool_list = []
            gmap_url = f'{add_url}/{zone_name}/gmap'
            json_data = {"ids": [ids],
                         "algorithm": random.choice(algorithm_list),
                         "gpool_list": gpool_list}
        except Exception as e:
            logger.error([f"edit addrr : {rname} not exist", get_code])
            return f"edit addrr : {rname} not exist", get_code
        try:
            resp, resp_code = self.put_response(url=gmap_url, auth=self.AUTH, data=json.dumps(json_data))
            assert resp_code == 200
            return resp, resp_code
        except Exception as e:
            logger.error([resp, resp_code])
            return resp, resp_code

    def delAddRR(self, zone_name, name_list=[], batchdel=False, current_user="admin"):
        '''del addrr'''
        if not isinstance(name_list, list):
            name_list = [name_list]
        ids = []
        unexist_addrr_template = []
        if batchdel:
            # 批量删除
            ids = self.getAllAddRR(zone_name)[0]
        else:
            for rname in name_list:
                try:
                    get_result, get_code = self.getAddRR(zone_name, rname)
                    if get_code == 500:
                        unexist_addrr_template.append(rname)
                    else:
                        assert get_code == 200
                        ids.append(get_result['resources'][0]['id'])
                except Exception as e:
                    logger.error(f"{rname} invalid not in addrr list")
        json_data = {"ids": ids, "current_user": current_user}
        gmap_url = f'{add_url}/{zone_name}/gmap'
        try:
            resp, resp_code = self.delete_response(url=gmap_url, auth=self.AUTH, data=json.dumps(json_data))
            resp_msg = f'{unexist_addrr_template} is ignored because they are not exist'
            assert resp_code == 200
            if unexist_addrr_template == []:
                return resp, resp_code
            return resp, resp_code, resp_msg
        except Exception as e:
            logger.error([f'delete addrr failed: {name_list} , info: {resp}', resp_code])
            return f'delete addrr failed: {name_list} , info: {resp}', resp_code

    def addRegion(self, name, current_user="admin"):
        '''add region'''
        json_data = {"name": name,
                     "current_user": current_user}
        try:
            resp, resp_code = self.post_response(url=region_url, auth=self.AUTH, data=json.dumps(json_data))
            assert resp_code == 200
            return resp, resp_code
        except Exception as e:
            logger.error(f'add region {name} failed---{resp}---{resp_code}')
            return resp, resp_code

    def getRegion(self, name):
        '''get region'''
        search_attrs = {"name": name}
        json_data = {"search_attrs": search_attrs}
        try:
            resp, resp_code = self.get_response(url=region_url, auth=self.AUTH, data=json.dumps(json_data))
            assert int(resp['total_size']) >= 1
            return resp, resp_code
        except Exception as e:
            logger.error([f'get region {name} failed', 500])
            return f'get region {name} failed', 500

    def getAllRegion(self):
        '''get all region'''
        ids = []
        try:
            resp_list, resp_code = self.get_response(url=region_url, auth=self.AUTH)
            assert resp_code == 200
            resources_list = resp_list["resources"]
            for resource in resources_list:
                ids.append(resource["id"])
            return ids, resp_code,
        except Exception as e:
            logger.error(["get region list error", resp_code])
            return "get region list error", resp_code

    def delRegion(self, name_list=[], batchdel=False, current_user="admin"):
        '''del region'''
        if not isinstance(name_list, list):
            name_list = [name_list]
        ids = []
        unexist_region_template = []
        if batchdel:
            # 批量删除
            ids = self.getAllRegion()[0]
        else:
            for name in name_list:
                try:
                    get_result, get_code = self.getRegion(name=name)
                    if get_code == 500:
                        unexist_region_template.append(name)
                    else:
                        assert get_code == 200
                        ids.append(get_result['resources'][0]['id'])
                except Exception as e:
                    logger.error(f"{name} invalid not in region list")
        json_data = {"ids": ids, "current_user": current_user}
        try:
            resp, resp_code = self.delete_response(url=region_url, auth=self.AUTH, data=json.dumps(json_data))
            resp_msg = f'{unexist_region_template} is ignored because they are not exist'
            assert resp_code == 200
            if unexist_region_template == []:
                return resp, resp_code
            return resp, resp_code, resp_msg
        except Exception as e:
            logger.error([f'delete region failed: {name_list} , info: {resp}', resp_code])
            return f'delete region failed: {name_list} , info: {resp}', resp_code

    def genMemberBody(self, mem_type, region_id=None, current_user="admin"):
        '''type_list = ["ip_subnet", "ip_range", "isp", "country", "province", "city", "region", "multi_and"]'''
        type_list = ["ip_subnet", "ip_range", "isp", "country", "province", "city", "region", "multi_and"]
        json_data = {"current_user": current_user}
        json_data['type'] = mem_type
        if mem_type == "ip_subnet":
            json_data["data1"] = f'{random.randint(15, 155)}.{random.randint(15, 155)}.{random.randint(15, 155)}.0/24'
        elif mem_type == "ip_range":
            json_data[
                "data1"] = f'{random.randint(100, 155)}.{random.randint(15, 155)}.{random.randint(15, 155)}.{random.randint(15, 155)}'
            json_data[
                "data2"] = f'{random.randint(156, 200)}.{random.randint(15, 155)}.{random.randint(15, 155)}.{random.randint(15, 155)}'
        elif mem_type == "isp":
            json_data["data1"] = f'{random.choice([0, 2, 3, 4, 6])}'
        elif mem_type == "country":
            json_data["data1"] = f'{random.randint(100, 200)}'
        elif mem_type == "province":
            json_data["data1"] = "1"
            json_data["data2"] = f'{random.randint(21, 34)}'
        elif mem_type == "city":
            json_data["data1"] = "1"
            json_data["data2"] = f'{random.choice([9, 10, 11, 13, 14, 15])}'
            json_data["data3"] = f'{random.randint(0, 4)}'
        elif mem_type == "region":
            region_list = self.getAllRegion()[0]
            if region_id in region_list:
                region_list.remove(region_id)
            if len(region_list) == 0:
                json_data["data1"] = ""
            else:
                json_data["data1"] = random.choice(region_list)
        elif mem_type == "multi_and":
            json_data["data1"] = "1"
            json_data["data2"] = f'{random.randint(16, 20)}'
            json_data["data3"] = f'{random.randint(0, 9)}'
            json_data["data4"] = f'{random.randint(0, 4)}'
        else:
            logger.error(f"member type {mem_type} unsupported, must be one of {type_list}")
            return f"member type {mem_type} unsupported, must be one of {type_list}"
        return json_data

    def addRegionMember(self, mem_type, region_id, current_user="admin"):
        '''add region member'''
        region_member_url = f'{region_url}/{region_id}/member'
        json_data = self.genMemberBody(mem_type, region_id, current_user)
        retry_time = 1
        if mem_type == "ip_subnet":
            while json_data["data1"] in self.getAllRegionMember(region_id)[2]:
                json_data = self.genMemberBody(mem_type, region_id, current_user)
        elif mem_type == "ip_range":
            while json_data["data1"] in self.getAllRegionMember(region_id)[2] and json_data["data2"] in \
                    self.getAllRegionMember(region_id)[3]:
                json_data = self.genMemberBody(mem_type, region_id, current_user)
        elif mem_type == "isp":
            while json_data["data1"] in self.getAllRegionMember(region_id)[2] and retry_time < 5:
                json_data = self.genMemberBody(mem_type, region_id, current_user)
                retry_time += 1
        elif mem_type == "country":
            while json_data["data1"] in self.getAllRegionMember(region_id)[2]:
                json_data = self.genMemberBody(mem_type, region_id, current_user)
        elif mem_type == "province":
            while json_data["data2"] in self.getAllRegionMember(region_id)[3] and retry_time < 5:
                json_data = self.genMemberBody(mem_type, region_id, current_user)
                retry_time += 1
        elif mem_type == "city":
            while json_data["data2"] in self.getAllRegionMember(region_id)[3] and json_data["data3"] in \
                    self.getAllRegionMember(region_id)[4] and retry_time < 5:
                json_data = self.genMemberBody(mem_type, region_id, current_user)
                retry_time += 1
        elif mem_type == "region":
            retry_time = 0
            while json_data["data1"] in self.getAllRegionMember(region_id)[2] and retry_time < 5:
                json_data = self.genMemberBody(mem_type, region_id, current_user)
                retry_time += 1
        elif mem_type == "multi_and":
            while json_data["data2"] in self.getAllRegionMember(region_id)[3] and json_data["data3"] in \
                    self.getAllRegionMember(region_id)[4] and json_data["data4"] in self.getAllRegionMember(region_id)[
                5] and retry_time < 5:
                json_data = self.genMemberBody(mem_type, region_id, current_user)
                retry_time += 1
        else:
            logger.error(f"member type {mem_type} unsupported")
            return f"member type {mem_type} unsupported"
        if retry_time == 5:
            logger.info(f'add region member type:{mem_type} failed, switch to "ip_subnet"')
            json_data = self.genMemberBody(mem_type="ip_subnet", region_id=region_id, current_user=current_user)
        try:
            resp, resp_code = self.post_response(url=region_member_url, auth=self.AUTH, data=json.dumps(json_data))
            assert resp_code == 200
            return resp, resp_code
        except Exception as e:
            logger.error(f'add region {region_id} member {mem_type} failed---{resp}---{resp_code}')
            return resp, resp_code

    def getRegionMember(self, region_id, region_member_id):
        '''get region member'''
        search_attrs = {"id": region_member_id}
        json_data = {"search_attrs": search_attrs}
        region_member_url = f'{region_url}/{region_id}/member'
        try:
            resp, resp_code = self.get_response(url=region_member_url, auth=self.AUTH, data=json.dumps(json_data))
            assert int(resp['total_size']) >= 1
            return resp, resp_code
        except Exception as e:
            logger.error([f'get region:{region_id} member:{region_member_id} failed', 500])
            return f'get region:{region_id} member:{region_member_id} failed', 500

    def getAllRegionMember(self, region_id):
        '''get all region member'''
        ids = []
        data1_list = []
        data2_list = []
        data3_list = []
        data4_list = []
        region_member_url = f'{region_url}/{region_id}/member'
        try:
            resp_list, resp_code = self.get_response(url=region_member_url, auth=self.AUTH)
            assert resp_code == 200
            resources_list = resp_list["resources"]
            for resource in resources_list:
                ids.append(resource["id"])
                if resource["data1"] != "":
                    data1_list.append(resource["data1"])
                if resource["data2"] != "":
                    data2_list.append(resource["data2"])
                if resource["data3"] != "":
                    data3_list.append(resource["data3"])
                if resource["data4"] != "":
                    data4_list.append(resource["data4"])
            return ids, resp_code, data1_list, data2_list, data3_list, data4_list
        except Exception as e:
            logger.error(["get region member list error", resp_code])
            return "get region member list error", resp_code

    def delRegionMember(self, region_id, name_list=[], batchdel=False, current_user="admin"):
        '''del region'''
        region_member_url = f'{region_url}/{region_id}/member'
        if not isinstance(name_list, list):
            name_list = [name_list]
        ids = []
        unexist_region_member_template = []
        if batchdel:
            # 批量删除
            ids = self.getAllRegionMember(region_id)[0]
        else:
            for name in name_list:
                try:
                    get_result, get_code = self.getRegionMember(region_id=region_id, region_member_id=name)
                    if get_code == 500:
                        unexist_region_member_template.append(name)
                    else:
                        assert get_code == 200
                        ids.append(get_result['resources'][0]['id'])
                except Exception as e:
                    logger.error(f"{name} invalid not in region member list")
        json_data = {"ids": ids, "current_user": current_user}
        try:
            resp, resp_code = self.delete_response(url=region_member_url, auth=self.AUTH, data=json.dumps(json_data))
            resp_msg = f'{unexist_region_member_template} is ignored because they are not exist'
            assert resp_code == 200
            if unexist_region_member_template == []:
                return resp, resp_code
            return resp, resp_code, resp_msg
        except Exception as e:
            logger.error([f'delete region member failed: {name_list} , info: {resp}', resp_code])
            return f'delete region member failed: {name_list} , info: {resp}', resp_code

    def addSpPolicy(self, logic="0", current_user="admin"):
        '''add sp policy'''
        dst_type = random.choice(["region", "ip_subnet"])
        if dst_type == "region":
            dst_data1 = random.choice(self.getAllRegion()[0])
        else:
            dst_data1 = f'{random.randint(15, 155)}.{random.randint(15, 155)}.{random.randint(15, 155)}.0/24'
        json_data = {"src_type": "region",
                     "src_logic": random.choice(["0", "1"]),
                     "src_data1": random.choice(self.getAllRegion()[0]),
                     "dst_type": dst_type,
                     "dst_logic": logic,
                     "dst_data1": dst_data1,
                     "current_user": current_user}
        while json_data in self.getAllSpPolicy()[3]:
            json_data["dst_type"] = "ip_subnet"
            json_data[
                "dst_data1"] = f'{random.randint(15, 155)}.{random.randint(15, 155)}.{random.randint(15, 155)}.0/24'

        try:
            resp, resp_code = self.post_response(url=sp_policy_url, auth=self.AUTH, data=json.dumps(json_data))
            assert resp_code == 200
            return resp, resp_code
        except Exception as e:
            logger.error(f'add sp policy failed---{resp}---{resp_code}')
            return resp, resp_code

    def getSpPolicy(self, sp_policy_id):
        '''get sp policy'''
        search_attrs = {"id": sp_policy_id}
        json_data = {"search_attrs": search_attrs}
        try:
            resp, resp_code = self.get_response(url=sp_policy_url, auth=self.AUTH, data=json.dumps(json_data))
            assert int(resp['total_size']) >= 1
            return resp, resp_code
        except Exception as e:
            logger.error([f'get sp policy:{sp_policy_id} failed', 500])
            return f'get sp policy:{sp_policy_id} failed', 500

    def getAllSpPolicy(self):
        '''get all sp policy'''
        ids = []
        used_region_list = []
        json_list = []
        json_dict = {}
        try:
            resp_list, resp_code = self.get_response(url=sp_policy_url, auth=self.AUTH)
            assert resp_code == 200
            resources_list = resp_list["resources"]
            for resource in resources_list:
                ids.append(resource["id"])
                used_region_list.append(resource["dst_data1"])
                json_dict["src_type"] = resource["src_type"]
                json_dict["src_logic"] = resource["src_logic"]
                json_dict["src_data1"] = resource["src_data1"]
                json_dict["dst_type"] = resource["dst_type"]
                json_dict["dst_logic"] = resource["dst_logic"]
                json_dict["dst_data1"] = resource["dst_data1"]
                json_dict["current_user"] = "admin"
                json_list.append(json_dict)
            return ids, resp_code, used_region_list, json_list
        except Exception as e:
            logger.error(["get sp policy list error", resp_code])
            return "get sp policy list error", resp_code

    def editSpPolicy(self, sp_policy_id):
        '''edit sp policy'''
        try:
            get_result, get_code = self.getSpPolicy(sp_policy_id)
            assert get_code == 200
        except Exception as e:
            logger.error([f"edit sp policy : id:{sp_policy_id} not exist: {get_result}", get_code])
            return f"edit sp policy : id:{sp_policy_id} not exist: {get_result}", get_code
        try:
            dst_type = random.choice(["region", "ip_subnet"])
            if dst_type == "region":
                dst_data1 = self.getAllRegion()[0]
                for used_region_id in self.getAllSpPolicy()[2]:
                    if used_region_id in dst_data1:
                        dst_data1.remove(used_region_id)
                if len(dst_data1) == 0:
                    dst_type = "ip_subnet"
                    dst_data1 = f'{random.randint(15, 155)}.{random.randint(15, 155)}.{random.randint(15, 155)}.0/24'
                else:
                    dst_data1 = random.choice(dst_data1)
            else:
                dst_data1 = f'{random.randint(15, 155)}.{random.randint(15, 155)}.{random.randint(15, 155)}.0/24'
            json_data = {"ids": [sp_policy_id],
                         "src_type": "region",
                         "src_logic": random.choice(["0", "1"]),
                         "src_data1": random.choice(self.getAllRegion()[0]),
                         "dst_type": dst_type,
                         "dst_logic": random.choice(["0", "1"]),
                         "dst_data1": dst_data1,
                         "priority": sp_policy_id}
            resp_code = self.put_response(url=sp_policy_url, auth=self.AUTH, data=json.dumps(json_data), int_data="sp")
            assert resp_code == 200
            return resp_code
        except Exception as e:
            logger.error([f"edit sp policy id: {sp_policy_id} failed", 500])
            return f"edit sp policy id: {sp_policy_id} failed", 500

    def delSpPolicy(self, name_list=[], batchdel=False, current_user="admin"):
        '''del sp policy'''
        if not isinstance(name_list, list):
            name_list = [name_list]
        ids = []
        unexist_sp_policy = []
        if batchdel:
            # 批量删除
            ids = self.getAllSpPolicy()[0]
        else:
            for name in name_list:
                try:
                    get_result, get_code = self.getSpPolicy(name)
                    if get_code == 500:
                        unexist_sp_policy.append(name)
                    else:
                        assert get_code == 200
                        ids.append(get_result['resources'][0]['id'])
                except Exception as e:
                    logger.error(f"{name} invalid not in sp policy list")
        json_data = {"ids": ids, "current_user": current_user}
        try:
            resp, resp_code = self.delete_response(url=sp_policy_url, auth=self.AUTH, data=json.dumps(json_data))
            resp_msg = f'{unexist_sp_policy} is ignored because they are not exist'
            assert resp_code == 200
            if unexist_sp_policy == []:
                return resp, resp_code
            return resp, resp_code, resp_msg
        except Exception as e:
            logger.error([f'delete sp policy failed: {name_list} , info: {e}', resp_code])
            return f'delete sp policy failed: {name_list} , info: {e}', resp_code

    def cleanGslbEnv(self):
        '''clean dns env'''
        try:
            logger.info("cleaning gslb env")
            self.delSpPolicy(batchdel=True)
            self.delRegion(batchdel=True)
            self.delAddZone(batchdel=True)
            self.delGpool(batchdel=True)
            self.delGmember(batchdel=True)
            self.delLink(batchdel=True)
            self.delAllSyngroup()
            self.delHm(batchdel=True)
            self.delAllDc()
            with open(log_file, 'r+') as file:
                file.truncate(0)
            logger.info("clean gslb finished")
        except Exception as e:
            logger.error(f'clean gslb env error!---{e}')


if __name__ == "__main__":
    GSLB = GSLBCommon()
    GSLB.addDc()
