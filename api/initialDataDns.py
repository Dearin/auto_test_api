# -*- coding: utf-8 -*-
import random
import sys

from api.DNSCommon import *

sys.path.append("../")
from jsonpath import jsonpath


class initialDataDns(DNSCommon):
    @useDebug
    def __init__(self, AUTH=(username, password), HOST_IP=master_ip, HOST_PORT=master_ip, LANG=lang):
        DNS = DNSCommon()
        # 控制模块数据是否初始化
        if Dns_Flag.lower() == "true":
            DNS.cleanDnsEnv()
        self.HOST_IP = HOST_IP
        self.HOST_PORT = HOST_PORT
        self.AUTH = AUTH
        self.LANG = LANG

    def addAcls(self):
        '''add acls'''
        acl_success_list = []
        acl_failed_list = []
        for num in range(acl_count):
            name = f'acl_{num}'
            network = [self.get_random_ip()]
            addAcl_result = self.addAcl(name, network)
            if addAcl_result[1] == 200:
                acl_success_list.append(name)
                logger.success(f'add acl: {name} network:{network} success')
            else:
                acl_failed_list.append(name)
                logger.error(f'add acl: {name} network:{network} failed')
        analysis_info = f'acl success count: {len(acl_success_list)} && acl fail count: {len(acl_failed_list)}'
        return acl_success_list, acl_failed_list, len(acl_success_list), len(acl_failed_list), analysis_info

    def addViews(self, acls):
        '''add views'''
        view_success_list = []
        view_failed_list = []
        for num in range(view_count):
            name = f'view_{num}'
            addview_result = self.addView(name, acls)
            if addview_result[1] == 200:
                view_success_list.append(name)
                logger.success(f'add view: {name} acl:{acls} success')
            else:
                view_failed_list.append(name)
                logger.error(f'add view: {name} acl:{acls} failed')
        analysis_info = f'view success count: {len(view_success_list)} && view fail count: {len(view_failed_list)}'
        return view_success_list, view_failed_list, len(view_success_list), len(view_failed_list), analysis_info

    def addTimes(self):
        ''' add time-strategies'''
        time_success_list = []
        time_fail_list = []
        for num in range(time_strategy_count):
            name = f'time_{num}'
            addTime_result = self.addTime(name)
            if addTime_result[1] == 200:
                time_success_list.append(name)
                logger.success(f'add time-strategy:{name} success ')
            else:
                time_fail_list.append(name)
                logger.error(f'add time-strategy : {name} failed')
        analysis_info = f'time-strategies success count: {len(time_success_list)} && view fail count: {len(time_fail_list)}'
        return time_success_list, time_fail_list, len(time_success_list), len(time_fail_list), analysis_info

    def addSmartLoads(self):
        '''add smartloads '''
        # 获取当前已有的 acls
        success, fail = 0, 0
        acls = []
        allAcls = self.getAllAcl()[0]
        allViews = self.getAllView()[0]
        acls.append(allAcls[0])
        count = view_count if smartloads_count > view_count else smartloads_count
        # if smartloads_count > view_count:
        #     count = view_count
        for num in range(count):
            # view 不能重复
            view = allViews[num]
            addSmartLoads_result = self.addSmartLoad(acls=acls, view=view)
            if addSmartLoads_result[1] == 200:
                logger.success(f'add smart-loads: acl:[{acls}],view:[{view}] success ')
                success += 1
            else:
                logger.error(f'add smart-loads: acl:[{acls}],view:[{view}] success ')
                fail += 1
        return success, fail

    def addDispatcherStras(self):
        ''' add dispatcher-strategies'''
        success_list = []
        fail_list = []
        for num in range(dispatcher_count):
            name = f'link_{num}'
            add_link_result = self.addDispatcherStra(name=name)
            if add_link_result[1] == 200:
                success_list.append(name)
                logger.success(f'add link dispatcher: {name} success')
            else:
                fail_list.append(name)
                logger.error(f'add link dispatcher: {name}  failed')
        return success_list, fail_list

    def addForwardGroups(self):
        '''add forwardgroups'''
        forwardGroup_success_list = []
        forwardGroup_failed_list = []
        for num in range(forwardGroup_count):
            name = f'forwardgroup_{num}'
            zone_servers_list = [self.get_random_ip(), self.get_random_ipv6_ip()]
            addForwardGroup_result = self.addForwardGroup(name, zone_servers_list)
            if addForwardGroup_result[1] == 200:
                forwardGroup_success_list.append(name)
                logger.success(f'add forwardGroup: {name} zone_servers_list:{zone_servers_list} success')
            else:
                forwardGroup_failed_list.append(name)
                logger.error(f'add forwardGroup: {name} zone_servers_list:{zone_servers_list} failed')
        analysis_info = f'forwardGroup success count: {len(forwardGroup_success_list)} && forwardGroup fail count: {len(forwardGroup_failed_list)}'
        return forwardGroup_success_list, forwardGroup_failed_list, len(forwardGroup_success_list), len(
            forwardGroup_failed_list), analysis_info

    def addForwardZones(self, name_type="domain", view=["default"], forward_style="First/RTT", servers=[],
                        servers_type="group"):
        '''add forwardzones'''
        forwardZone_success_list = []
        forwardZone_failed_list = []
        for num in range(forwardZone_count):
            name = f'forwardgzone_{num}.{self.get_random_zone()}{self.get_random_zone()}'
            addForwardZone_result = self.addForwardZone(name=name, name_type=name_type, view=view,
                                                        forward_style=forward_style, servers=servers,
                                                        servers_type=servers_type)
            if addForwardZone_result[1] == 200:
                forwardZone_success_list.append(name)
                logger.success(f'add forwardZones: {name} forward_to:{servers} success')
            else:
                forwardZone_failed_list.append(name)
                logger.error(f'add forwardZones: {name} forward_to:{servers} failed')
        view_forwardZone_success_count = len(forwardZone_success_list)
        view_forwardZone_fail_count = len(forwardZone_failed_list)
        forwardZone_success_count = view_forwardZone_success_count * (view_count + 1)
        forwardZone_fail_count = view_forwardZone_fail_count * (view_count + 1)
        analysis_info = f'forwardZones success count: {forwardZone_success_count} && forwardZones fail count: {forwardZone_fail_count}'
        return forwardZone_success_list, forwardZone_failed_list, forwardZone_success_count, forwardZone_fail_count, analysis_info

    def addZones(self, view_list=["default"]):
        '''add zones'''
        zone_success_list = []
        zone_failed_list = []
        default_zonelist = []
        for view in view_list:
            for num in range(random_zone_count):
                zone_name = self.get_random_zone()
                addzone_result = self.addZone(name=zone_name, view=view)
                if addzone_result[1] == 200:
                    if view == "default":
                        default_zonelist.append(zone_name)
                    zone_success_list.append(zone_name)
                    logger.success(f'add zone: {zone_name} view:{view} success')
                else:
                    zone_failed_list.append(zone_name)
                    logger.error(f'add zone: {zone_name} view:{view} failed')
        analysis_info = f'zone success count: {len(zone_success_list)} && zone fail count: {len(zone_failed_list)}'
        return zone_success_list, zone_failed_list, default_zonelist, len(zone_success_list), len(
            zone_failed_list), len(default_zonelist), analysis_info

    def addZonesRRs(self):
        '''add zonerrs'''
        viewzone_success_list = []
        viewzone_failed_list = []
        default_zonelist = []
        import_default_zonelist = []
        import_fail_default_zonelist = []
        view_rr_success_count = 0
        view_rr_fail_count = 0
        # import view zone
        self.generate_view_zone_file()

        view_list = os.listdir(zone_path)
        for view in view_list:
            if view == "default":
                # import default zone
                default_file_list = os.listdir(f'{zone_path}/{view}')
                for file in default_file_list:
                    file_with_path = f'{zone_path}/{view}/{file}'
                    zone_name = file.rsplit('.', 1)[0].split('_')[1]
                    zone_base64 = self.get_zone_param(file_with_path)
                    addzone_result = self.addZoneFile(name=zone_name, zone_base64=zone_base64)
                    if addzone_result[1] == 200:
                        logger.success(f'import {view} zone file.........{file} success')
                        import_default_zonelist.append(zone_name)
                    else:
                        logger.error(f'import {view} zone file.........{file} failed')
                        import_fail_default_zonelist.append(zone_name)

            elif "view" in view:
                view_file_list = os.listdir(f'{zone_path}/{view}')
                for file in view_file_list:
                    file_with_path = f'{zone_path}/{view}/{file}'
                    zone_name = file.rsplit('.', 1)[0].split('_')[1]
                    zone_base64 = self.get_zone_param(file_with_path)
                    addzone_result = self.addZoneFile(name=zone_name, view=view, zone_base64=zone_base64)
                    if addzone_result[1] == 200:
                        logger.success(f'import {view} zone file.........{file} success')
                        viewzone_success_list.append(zone_name)
                        view_rr_success_count += random_rr_count
                    else:
                        logger.error(f'import {view} zone file.........{file} failed')
                        viewzone_failed_list.append(zone_name)
                        view_rr_fail_count += random_rr_count

        rr_success_count = len(import_default_zonelist) * per_zone_rr_count + view_rr_success_count
        rr_fail_count = len(import_fail_default_zonelist) * per_zone_rr_count + view_rr_fail_count
        analysis_info = f'zone import count: {len(default_zonelist)}, zone success count: {len(viewzone_success_list)} && zone fail count: {len(viewzone_success_list)}'
        return viewzone_success_list, viewzone_failed_list, default_zonelist, len(viewzone_success_list), len(
            viewzone_failed_list), len(default_zonelist), len(import_default_zonelist), len(
            import_fail_default_zonelist), rr_success_count, rr_fail_count, analysis_info

    def addDomains(self):
        domain_success_list = []
        domain_fail_list = []
        '''get all domainnames '''
        for num in range(domain_name_count):
            domain_names = []
            domain_name = f'domain_{num}'
            domain_names.append(domain_name)
            addDomain_result = self.addDomain('游戏网站', domain_names)
            if addDomain_result[1] == 200:
                domain_success_list.append(domain_name)
                logger.success(f'add domainnames: [{domain_name}] success')
            else:
                domain_fail_list.append(domain_name)
                logger.error(f'add domainnames:[{domain_name}]fail')
        analysis_info = f'domainnames success count: {len(domain_success_list)} && domainnames fail count: {len(domain_fail_list)}'
        return domain_success_list, domain_fail_list, len(domain_success_list), len(domain_fail_list), analysis_info

    def addTriggers(self,type='analysis-link'): # -- 需优化
        """
        Trigger-strategies新增type为 dynamic-load 的 trigger 调度时，需要 2+以上的 dispatcher-strategies,
        且这些 dispatcher-strategies 所依赖的view视图不能为同一个。
        addTrigger(self, name, link_mapping, response_link, type, dispatch_object=['游戏网站'])
        - dunamic-load 类型的 trigger 数据新增，还需要优化
        """
        success_list = []
        failed_list = []
        links_names = []
        links = self.queryAllDispatcherStrObjs()[0]['resources']
        for link in links:
            links_names.append(link['name'])

        for num in range(trigger_count):
            name = f'trigger_{num}'
            try:
                resp, resp_code = self.addTrigger(name=name,link_mapping=random.choice(links_names),type=type)
                assert resp_code == 200
                return resp, resp_code
            except Exception as e:
                logger.error([resp, resp_code])
                return resp, resp_code
        for num in trigger_count:
            name = f'trigger_{num}'


    def addViewRRs(self, zone_name, view):
        '''add rrs'''
        rr_success_list = []
        rr_failed_list = []
        for num in range(random_rr_count):
            generate_rr_result = self.generate_random_rrset(rtype_list[random.randint(0, len(rtype_list) - 1)])
            rname = generate_rr_result['name']
            rtype = generate_rr_result['type']
            ttl = generate_rr_result['ttl']
            rdata = generate_rr_result['rdata']
            addrr_result = self.addRR(zone_name=zone_name, view=view, rname=rname, rtype=rtype, ttl=ttl, rdata=rdata)
            if addrr_result[1] == 200:
                rr_success_list.append(rname)
                logger.success(f'view:{view} add rr: {rname}{zone_name} type:{rtype}  rdata:{rdata} success')
            else:
                rr_failed_list.append(rname)
                logger.error(f'view:{view} add rr: {rname}{zone_name} type:{rtype}  rdata:{rdata} failed')
        analysis_info = f'rr success count: {len(rr_success_list)} && rr fail count: {len(rr_failed_list)}'
        return rr_success_list, rr_failed_list, len(rr_success_list), len(rr_failed_list), analysis_info

    @useDebug
    def acl_loop(self):
        acl_name = f'acl_loop_{random.randint(1, 9999)}'
        network_list = [self.get_random_ip(), self.get_random_ip()]
        update_network_list = [self.get_random_ip(), self.get_random_ip()]
        add_result = self.addAcl(acl_name, network_list)
        get_result = self.getAcl(acl_name)
        edit_result = self.editAcl(acl_name, update_network_list)
        del_result = self.delAcl([acl_name])

    @useDebug
    def view_loop(self):
        view_name = f'view_loop_{random.randint(1, 9999)}'
        acl_list = []
        update_acl_list = self.getAllAcl()[0]
        add_result = self.addView(view_name, acl_list)
        get_result = self.getView(view_name)
        edit_result = self.editView(view_name, update_acl_list)
        del_result = self.delView([view_name])

    @useDebug
    def forwardGroup_loop(self):
        forwardGroup_name = f'forwardgroup_loop_{random.randint(1, 9999)}'
        network_list = [self.get_random_ip(), self.get_random_ip()]
        update_network_list = [self.get_random_ip(), self.get_random_ip()]
        add_result = self.addForwardGroup(forwardGroup_name, network_list)
        get_result = self.getForwardGroup(forwardGroup_name)
        edit_result = self.editForwardGroup(forwardGroup_name, update_network_list)
        del_result = self.delForwardGroup([forwardGroup_name])

    @useDebug
    def forwardZone_loop(self):
        forwardZone_name = f'forwardzone_loop_{random.randint(1, 9999)}'
        network_list = [self.get_random_ip(), self.get_random_ip()]
        update_network_list = [self.get_random_ip(), self.get_random_ip()]
        add_result = self.addForwardZone(name=forwardZone_name, servers=network_list)
        get_result = self.getForwardZone(forwardZone_name)
        #         edit_result = self.editForwardZone(forwardZone_name, update_network_list)
        del_result = self.delForwardZone(name_list=[forwardZone_name])

    @useDebug
    def zone_rrs_loop(self):
        zone_name = f'zone_loop_{random.randint(1, 9999)}'
        rset = self.generate_random_rrset(rtype_list[random.randint(0, len(rtype_list) - 1)])
        rname = rset["name"]
        rtype = rset['type']
        ttl = rset['ttl']
        rdata = rset['rdata']
        add_zone_result = self.addZone(zone_name)
        get_zone_result = self.getZone(zone_name)

        add_rr_result = self.addRR(zone_name, rname=rname, rtype=rtype, ttl=ttl, rdata=rdata)
        get_rr_result = self.getRR(zone_name, rname=rname, rtype=rtype)
        edit_rr_result = self.editRR(zone_name, rname=rname, rdata=rdata, rtype=rtype, ttl="521")

        edit_zone_result = self.editZone(zone_name, default_ttl="521")
        del_rr_result = self.delRR(zone_name, rname_list=[rname], rtype=edit_rr_result[0][0]['type'])
        del_zone_result = self.delZone([zone_name])

    def rrs_loop(self):
        zone_name = 'city1.provb.node.epc.mnc000.mcc460.3gppnetwork.org0'
        rset = self.generate_random_rrset(rtype_list[random.randint(0, len(rtype_list) - 1)])
        rname = rset["name"]
        rtype = rset['type']
        ttl = rset['ttl']
        rdata = rset['rdata']

        add_rr_result = self.addRR(zone_name, rname=rname, rtype=rtype, ttl=ttl, rdata=rdata)
        get_rr_result = self.getRR(zone_name, rname=rname, rtype=rtype)
        edit_rr_result = self.editRR(zone_name, rname=rname, rdata=rdata, rtype=rtype, ttl="521")
        del_rr_result = self.delRR(zone_name, rname_list=[rname], rtype=edit_rr_result[0][0]['type'])

    @useDebug
    def addDnsData(self):
        acl_result = self.addAcls()
        view_result = self.addViews(acl_result[0])
        view_result[0].append("default")
        forwardGroup_result = self.addForwardGroups()
        forwardZone_result = self.addForwardZones(view=view_result[0], servers=forwardGroup_result[0])
        zone_result = self.addZonesRRs()
        logger.info(f'acl success count {acl_result[2]}, acl fail count {acl_result[3]}')
        logger.info(f'view success count {view_result[2]}, view fail count {view_result[3]}')
        logger.info(
            f'forwardGroup success count {forwardGroup_result[2]}, forwardGroup fail count {forwardGroup_result[3]}')
        logger.info(
            f'forwardZone success count {forwardZone_result[2]}, forwardZone fail count {forwardZone_result[3]}')
        logger.info(f'view zone success count {zone_result[3]}, view zone fail count {zone_result[4]}')
        logger.info(f'rrs success count {zone_result[8]}, rrc fail count {zone_result[9]}')
        logger.info(
            f'default zone import success count {zone_result[6]}, default zone import fail count {zone_result[7]}')

        keylist = ['ACL', 'VIEW', '转发组', '转发区', 'default区导入', 'view区导入', '记录']
        success_valuelist = [acl_result[2], view_result[2], forwardGroup_result[2], forwardZone_result[2],
                             zone_result[6], zone_result[3], zone_result[8]]
        fail_valuelist = [acl_result[3], view_result[3], forwardGroup_result[3], forwardZone_result[3], zone_result[7],
                          zone_result[4], zone_result[9]]
        return keylist, success_valuelist, fail_valuelist
