# -*- coding: utf-8 -*-
from conf.zdns_param import *
from loguru import logger
import configparser
import os, platform, shutil

parent_dir = os.getcwd()
print(parent_dir)
cf = configparser.ConfigParser()
# cf.read("../../stability_191.ini", encoding="utf-8")
cf.read("/opt/auto_test_api/conf/data_config.ini", encoding="utf-8")
###------------------test-items------------------###

Dns_Flag = cf.get("test-items", "Dns_Flag").strip()
Gslb_Flag = cf.get("test-items", "Gslb_Flag").strip()
Dhcp_Flag = cf.get("test-items", "Dhcp_Flag").strip()

### ------------------base-data------------------ ###
# 解析管理 - 访问控制模块
acl_count = int(cf.get("base-data", "acl_count").strip())
view_count = int(cf.get("base-data", "view_count").strip())
domain_name_count = int(cf.get("base-data", "domain_name_count").strip())
time_strategy_count = int(cf.get("base-data", "time_strategy_count").strip())

# 解析管理 - 递归调度模块
smartloads_count = int(cf.get("base-data", "smartloads_count").strip())
dispatcher_count = int(cf.get("base-data", "dispatcher_count").strip())
trigger_count =  int(cf.get("base-data", "trigger_count").strip())


forwardGroup_count = int(cf.get("base-data", "forwardGroup_count").strip())
forwardZone_count = int(cf.get("base-data", "forwardZone_count").strip())
random_zone_count = int(cf.get("base-data", "random_zone_count").strip())
random_rr_count = int(cf.get("base-data", "random_rr_count").strip())
zone_path = test_case_dir = f'{parent_dir}/zone'
per_zone_rr_count = int(cf.get("base-data", "per_zone_rr_count").strip())
hm_icmp_count = int(cf.get("base-data", "hm_icmp_count").strip())
hm_tcp_count = int(cf.get("base-data", "hm_tcp_count").strip())
hm_http_count = int(cf.get("base-data", "hm_http_count").strip())
link_count = int(cf.get("base-data", "link_count").strip())
gpool_count = int(cf.get("base-data", "gpool_count").strip())
add_zone_count = int(cf.get("base-data", "add_zone_count").strip())
add_rr_count = int(cf.get("base-data", "add_zone_count").strip())
region_count = int(cf.get("base-data", "region_count").strip())
sp_policy_count = int(cf.get("base-data", "sp_policy_count").strip())



###------------------rtype-list------------------###
rtype_list = ["A", "AAAA", "MX", "NS", "CNAME", "NAPTR", "SRV", "PTR", "TXT", "DNAME", "SPF", "CAA"]
import_rtype_list = ["A", "AAAA", "NS", "CNAME", "PTR", "TXT", "DNAME", "SPF"]

###------------------local-env------------------###
auto_install = cf.get("local-env", "auto_install")

runname = cf.get("local-env", "runname").strip()
runtime = cf.get("local-env", "runtime").strip()
api_looptime = cf.get("local-env", "api_looptime").strip()

dns_node = [cf.get("local-env", "dns_node").replace(' ', '').replace('[', '').replace(']', '').replace('"', '')][
    0].split(',')

master_ip = cf.get("local-env", "master_ip").strip()
master_query_port = cf.get("local-env", "master_query_port").strip()
master_api_port = cf.get("local-env", "master_api_port").strip()
master_ssh_port = cf.get("local-env", "master_ssh_port").strip()

ssh_user = cf.get("local-env", "ssh_user").strip()
ssh_passwd = cf.get("local-env", "ssh_passwd").strip()

slave = cf.get("local-env", "slave").strip()
slave_ip = cf.get("local-env", "slave_ip").strip()
slave_query_port = cf.get("local-env", "slave_query_port").strip()
slave_api_port = cf.get("local-env", "slave_api_port").strip()
slave_ssh_port = cf.get("local-env", "slave_ssh_port").strip()
slave_ssh_user = cf.get("local-env", "slave_ssh_user").strip()
slave_ssh_passwd = cf.get("local-env", "slave_ssh_passwd").strip()

slave2 = cf.get("local-env", "slave2").strip()
slave2_ip = cf.get("local-env", "slave2_ip").strip()
slave2_query_port = cf.get("local-env", "slave2_query_port").strip()
slave2_api_port = cf.get("local-env", "slave2_api_port").strip()
slave2_ssh_port = cf.get("local-env", "slave2_ssh_port").strip()
slave2_ssh_user = cf.get("local-env", "slave2_ssh_user").strip()
slave2_ssh_passwd = cf.get("local-env", "slave2_ssh_passwd").strip()

client_ip = cf.get("local-env", "client_ip").strip()
client_ssh_port = cf.get("local-env", "client_ssh_port").strip()
client_ssh_user = cf.get("local-env", "client_ssh_user").strip()
client_ssh_passwd = cf.get("local-env", "client_ssh_passwd").strip()

monitor1 = cf.get("local-env", "monitor1").strip()
monitor1_name = cf.get("local-env", "monitor1_name").strip()
monitor1_ip = cf.get("local-env", "monitor1_ip").strip()
monitor1_query_port = cf.get("local-env", "monitor1_query_port").strip()
monitor1_api_port = cf.get("local-env", "monitor1_api_port").strip()
monitor1_ssh_port = cf.get("local-env", "monitor1_ssh_port").strip()
monitor1_ssh_user = cf.get("local-env", "monitor1_ssh_user").strip()
monitor1_ssh_passwd = cf.get("local-env", "monitor1_ssh_passwd").strip()

monitor2 = cf.get("local-env", "monitor2").strip()
monitor2_name = cf.get("local-env", "monitor2_name").strip()
monitor2_ip = cf.get("local-env", "monitor2_ip").strip()
monitor2_query_port = cf.get("local-env", "monitor2_query_port").strip()
monitor2_api_port = cf.get("local-env", "monitor2_api_port").strip()
monitor2_ssh_port = cf.get("local-env", "monitor2_ssh_port").strip()
monitor2_ssh_user = cf.get("local-env", "monitor2_ssh_user").strip()
monitor2_ssh_passwd = cf.get("local-env", "monitor2_ssh_passwd").strip()

monitor3 = cf.get("local-env", "monitor3").strip()
monitor3_name = cf.get("local-env", "monitor3_name").strip()
monitor3_ip = cf.get("local-env", "monitor3_ip").strip()
monitor3_query_port = cf.get("local-env", "monitor3_query_port").strip()
monitor3_api_port = cf.get("local-env", "monitor3_api_port").strip()
monitor3_ssh_port = cf.get("local-env", "monitor3_ssh_port").strip()
monitor3_ssh_user = cf.get("local-env", "monitor3_ssh_user").strip()
monitor3_ssh_passwd = cf.get("local-env", "monitor3_ssh_passwd").strip()

username = cf.get("local-env", "username").strip()
password = cf.get("local-env", "password").strip()

debug_tag = cf.get("local-env", "debug_tag").strip()

###------------------[BaseDir]--------------------###
zddi_dir = cf.get("BaseDir", "zddi_dir").strip()
if "appdata" in zddi_dir:
    database_dir = f'{zddi_dir}/data/zddi'
    dns_etc_dir = f'{database_dir}/etc'
    zddi_log_dir = f'{zddi_dir}/log'
else:
    database_dir = f'{zddi_dir}/zddi'
    dns_etc_dir = f'{zddi_dir}/zddi/dns/etc'
    zddi_log_dir = zddi_dir

###------------------test-log------------------###
log_dir = f'{parent_dir}/log'
upload_path = f'{parent_dir}/upload'
log_file = '/opt/auto_test_api/log/initialData.log'

###------------------test-case-dir------------------###
test_case_dir = f'{parent_dir}/src/testcases/'

###------------------Mail------------------###
mail_receiver = [cf.get("Mail", "mail_receiver").replace(' ', '').replace('[', '').replace(']', '').replace('"', '')][
    0].split(',')
mail_repeat_times = int(cf.get("Mail", "mail_repeat_times").strip())

###------------------dnsperf-param------------------###
client_count = int(cf.get("dnsperf-param", "client_count").strip())
max_num_qps = int(cf.get("dnsperf-param", "max_num_qps").strip())
print_qps = int(cf.get("dnsperf-param", "print_qps").strip())
qps_limit = int(cf.get("dnsperf-param", "qps_limit").strip())
slave_qps_limit = int(cf.get("dnsperf-param", "slave_qps_limit").strip())
slave2_qps_limit = int(cf.get("dnsperf-param", "slave2_qps_limit").strip())
monitor1_qps_limit = int(cf.get("dnsperf-param", "monitor1_qps_limit").strip())
monitor2_qps_limit = int(cf.get("dnsperf-param", "monitor2_qps_limit").strip())
monitor3_qps_limit = int(cf.get("dnsperf-param", "monitor3_qps_limit").strip())
time_out = int(cf.get("dnsperf-param", "time_out").strip())
# qpdata_local = cf.get("dnsperf-param", "qpdata_local")
# qpdata_client = cf.get("dnsperf-param", "qpdata_client")

upload_path = test_case_dir = f'{parent_dir}/upload'
# remote_dir = cf.get("dnsperf-param", "remote_dir")
# remote_dnsperf = cf.get("dnsperf-param", "remote_dnsperf")

qpdata_local = 'dnsperf.txt'
qpdata_client = '/root/dnsperf.txt'
if Dns_Flag.lower() != "true":
    qpdata_local = 'dnsperf_gslb_only.txt'

remote_dir = '/root'
remote_dnsperf = '/root/dnsperf'

lang = "zh"
headers = {'Content-Type': 'application/json'}

## api 相关的 url
base_url = f"https://{master_ip}:{master_api_port}/"

# 解析管理 - 访问控制模块
acl_url = f"https://{master_ip}:{master_api_port}/acls"
view_url = f"https://{master_ip}:{master_api_port}/views"
domain_url = f"https://{master_ip}:{master_api_port}/domainname-names"
time_strategies_url = f"https://{master_ip}:{master_api_port}/time_strategies"

# 智能负载模块
smart_loads_url = f"https://{master_ip}:{master_api_port}/smart-loads"
dispatcher_url = f"https://{master_ip}:{master_api_port}/dispatcher-strategies"
trigger_url = f"https://{master_ip}:{master_api_port}/trigger-strategies"

forwardgroup_url = f"https://{master_ip}:{master_api_port}/zone_server_groups"
forwardzone_url = f"https://{master_ip}:{master_api_port}/forward-zones"
resolutionSuccessRate_url = f"https://{master_ip}:{master_api_port}/stats/6/groups/*/members/*/views/*/%E8%A7%A3%E6%9E%90%E6%88%90%E5%8A%9F%E7%8E%87"
monitor1_resolutionSuccessRate_url = f"https://{monitor1_ip}:{monitor1_api_port}/stats/6/groups/*/members/*/views/*/%E8%A7%A3%E6%9E%90%E6%88%90%E5%8A%9F%E7%8E%87"
monitor2_resolutionSuccessRate_url = f"https://{monitor2_ip}:{monitor2_api_port}/stats/6/groups/*/members/*/views/*/%E8%A7%A3%E6%9E%90%E6%88%90%E5%8A%9F%E7%8E%87"
monitor3_resolutionSuccessRate_url = f"https://{monitor3_ip}:{monitor3_api_port}/stats/6/groups/*/members/*/views/*/%E8%A7%A3%E6%9E%90%E6%88%90%E5%8A%9F%E7%8E%87"

dc_url = f"https://{master_ip}:{master_api_port}/dc"
hm_template_url = f"https://{master_ip}:{master_api_port}/hm_template"
link_url = f"https://{master_ip}:{master_api_port}/link"
syngroup_url = f"https://{master_ip}:{master_api_port}/syngroup"
gpool_url = f"https://{master_ip}:{master_api_port}/gpool"
add_url = f"https://{master_ip}:{master_api_port}/views/ADD/dzone"
region_url = f"https://{master_ip}:{master_api_port}/region"
sp_policy_url = f"https://{master_ip}:{master_api_port}/sp_policy"

logger.add(log_file)

# def putPyechartsJson():
#     if "windows" in platform.system().lower():
#         json_path = 'C:\\pyecharts'
#     else:
#         json_path = '/tmp/pyecharts'
#     if os.path.exists(json_path) is False:
#         shutil.copytree(f'{upload_path}/pyecharts', json_path)
#         logger.success(f'pyecharts copy to {json_path} success')
#     return json_path
#
#
# json_path = putPyechartsJson()
