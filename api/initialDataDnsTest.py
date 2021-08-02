import random

from api.initialDataDns import initialDataDns
from loguru import logger


class initialDataTest:

    def __init__(self):
        self.dns = initialDataDns()

    def start(self):
        ''' 访问控制模块'''
        acls = []
        # 添加地址调度对象数据 - acl_count
        self.dns.addAcls()
        # 添加视图管理列表数据 - view_count
        allacls = list(self.dns.getAllAcl()[0]);
        logger.info("currentAcls contains: " + str(allacls))
        random_num = random.randint(0, len(allacls) - 1)
        acls.append(allacls[random_num])
        logger.info('addViewa - alcs - ' + str(acls))
        self.dns.addViews(acls)
        # 添加域名调度对象数据 - domain_name_count
        self.dns.addDomains()
        # 添加时间调度对象数据 - time_strategy_count
        self.dns.addTimes()
        ''' 递归调度模块 '''
        # 添加智能负载 - smartloads_count
        ## 调度模块需要在访问控制模块之后进行创建
        self.dns.addSmartLoads()
        # 添加链路映射 - dispatcher_count
        self.dns.addDispatcherStras()
        # 添加Trigger 调度
        self.dns.addTriggers()



    def test(self):
        print(self.dns.delAllTriggers())




if __name__ == '__main__':
    init = initialDataTest()
    init.test()
