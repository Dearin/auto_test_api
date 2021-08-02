# # -*-coding: utf-8-*-
# import sys
#
# from loguru import logger
#
# sys.path.append("../")
# from utils.RemoteModule import *
# from api.DNSCommon import *
# import csv
# import pandas as pd
# import numpy as np
# from pyecharts.charts import Line
# from pyecharts.charts import Bar
# from pyecharts.charts import Pie
# import pyecharts.options as opts
#
#
# class Util():
#
#     def __init__(self):
#         self.RM_master = RemoteModule(master_ip, master_ssh_port, ssh_user, ssh_passwd, log_dir, remote_dir)
#         self.RM_client = RemoteModule(client_ip, client_ssh_port, client_ssh_user, client_ssh_passwd, upload_path,
#                                       remote_dnsperf)
#         self.RM_monitor1 = RemoteModule(monitor1_ip, monitor1_ssh_port, monitor1_ssh_user, monitor1_ssh_passwd, log_dir,
#                                         remote_dir)
#         self.RM_monitor2 = RemoteModule(monitor2_ip, monitor2_ssh_port, monitor2_ssh_user, monitor2_ssh_passwd, log_dir,
#                                         remote_dir)
#         self.RM_monitor3 = RemoteModule(monitor3_ip, monitor3_ssh_port, monitor3_ssh_user, monitor3_ssh_passwd, log_dir,
#                                         remote_dir)
#         self.DNS = DNSCommon()
#
#     def is_number(self, s):
#         try:
#             float(s)
#             return True
#         except ValueError:
#             pass
#
#         try:
#             import unicodedata
#             unicodedata.numeric(s)
#             return True
#         except (TypeError, ValueError):
#             pass
#
#         return False
#
#     def exec_shell_cmd(self, shell_cmd):
#         print("---------------", shell_cmd)
#         result = os.popen(shell_cmd).read().strip()
#         return result
#
#     def getCmdCount(self):
#         try:
#             cmd_count = self.RM_master.exec_cmd(f'sqlite3 {database_dir}/clouddns.db "select count(*) from commands;"')
#             if self.is_number(cmd_count):
#                 return int(cmd_count)
#             else:
#                 return 1
#         except Exception as e:
#             logger.error(f'get cmd count failed --- {e}')
#
#     def getAlarmDbCount(self, start_time, end_time):
#         try:
#             cmd_count = self.RM_master.exec_cmd(
#                 f'sqlite3 {database_dir}/alarm.db "select count(*) from alarmlog where time>="{start_time}" and time <="{end_time}";"')
#             return int(cmd_count)
#         except Exception as e:
#             logger.error(f'get alarm db count failed --- {e}')
#
#     def getLogErrorCount(self):
#         error_log_file_list = ["clouddns*.log", "dns*.log", "monitor*.log", "probed.log", "system0*.log",
#                                "zva*.log", "log*.log", "node0*.log", "alarm*.log", "rsync.log"]
#         clouddns_error_count = self.RM_master.exec_cmd(
#             f'cat {zddi_log_dir}/clouddns*.log | grep ERROR | wc -l').replace('\n', '')
#         dns_error_count = self.RM_master.exec_cmd(f'cat {zddi_log_dir}/dns*.log | grep ERROR | wc -l').replace('\n', '')
#         monitor_error_count = self.RM_master.exec_cmd(f'cat {zddi_log_dir}/monitor*.log | grep ERROR | wc -l').replace(
#             '\n', '')
#         probed_error_count = self.RM_master.exec_cmd(f'cat {zddi_log_dir}/probed.log | grep ERROR | wc -l').replace(
#             '\n', '')
#         system_error_count = self.RM_master.exec_cmd(f'cat {zddi_log_dir}/system00*.log | grep ERROR | wc -l').replace(
#             '\n', '')
#         zva_error_count = self.RM_master.exec_cmd(f'cat {zddi_log_dir}/zva*.log | grep ERROR | wc -l').replace('\n', '')
#         log_error_count = self.RM_master.exec_cmd(f'cat {zddi_log_dir}/log*.log | grep ERROR | wc -l').replace('\n', '')
#         node_error_count = self.RM_master.exec_cmd(f'cat {zddi_log_dir}/node00*.log | grep ERROR | wc -l').replace('\n',
#                                                                                                                    '')
#         alarm_error_count = self.RM_master.exec_cmd(f'cat {zddi_log_dir}/alarm*.log | grep ERROR | wc -l').replace('\n',
#                                                                                                                    '')
#         if "appdata" in zddi_dir:
#             rsync_error_count = self.RM_master.exec_cmd(f'cat {zddi_log_dir}/rsync*.log | grep ERROR | wc -l').replace(
#                 '\n', '')
#         else:
#             rsync_error_count = self.RM_master.exec_cmd(
#                 f'cat {zddi_log_dir}/rsync/rsync*.log | grep ERROR | wc -l').replace('\n', '')
#         error_count_list = [clouddns_error_count, dns_error_count, monitor_error_count, probed_error_count,
#                             system_error_count, zva_error_count, log_error_count, node_error_count,
#                             alarm_error_count, rsync_error_count]
#         return error_log_file_list, error_count_list
#
#     def getSystemEnv(self, roll="master"):
#         if roll == "master":
#             master_kernel = self.RM_master.exec_cmd('uname -r')
#             client_kernel = self.RM_client.exec_cmd('uname -r')
#             if "el6" in str(master_kernel):
#                 master_system = "CENTOS6"
#             elif "ky10" in str(master_kernel):
#                 master_system = "KYLIN10"
#             else:
#                 master_system = "CENTOS7"
#             if "el6" in str(client_kernel):
#                 client_system = "CENTOS6"
#             elif "ky10" in str(client_kernel):
#                 master_system = "KYLIN10"
#             else:
#                 client_system = "CENTOS7"
#             return master_system, client_system
#         elif roll == "monitor1":
#             monitor1_kernel = self.RM_monitor1.exec_cmd('uname -r')
#             if "el6" in str(monitor1_kernel):
#                 monitor1_system = "CENTOS6"
#             elif "ky10" in str(monitor1_kernel):
#                 monitor1_system = "KYLIN10"
#             else:
#                 monitor1_system = "CENTOS7"
#             return monitor1_system
#         elif roll == "monitor2":
#             monitor2_kernel = self.RM_monitor2.exec_cmd('uname -r')
#             if "el6" in str(monitor2_kernel):
#                 monitor2_system = "CENTOS6"
#             elif "ky10" in str(monitor2_kernel):
#                 monitor2_system = "KYLIN10"
#             else:
#                 monitor2_system = "CENTOS7"
#             return monitor2_system
#         elif roll == "monitor3":
#             monitor3_kernel = self.RM_monitor3.exec_cmd('uname -r')
#             if "el6" in str(monitor3_kernel):
#                 monitor3_system = "CENTOS6"
#             elif "ky10" in str(monitor3_kernel):
#                 monitor3_system = "KYLIN10"
#             else:
#                 monitor3_system = "CENTOS7"
#             return monitor3_system
#
#     def genLogFiles(self, log_dir=log_dir):
#         log_files_dict = {}
#         localtime = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(time.time()))
#         log_files_dict['localtime'] = localtime
#         log_files_dict['stability_log_dir'] = f'{log_dir}/stability_{localtime}'
#         if os.path.exists(log_files_dict['stability_log_dir']) is False:
#             os.makedirs(log_files_dict['stability_log_dir'])
#         log_files_dict['glancecsv_filename'] = f'glances_{localtime}.csv'
#         log_files_dict['remote_glancecsv_filename_with_path'] = f'/tmp/glances_{localtime}.csv'
#         log_files_dict[
#             'local_glancecsv_filename_with_path'] = f'{log_files_dict["stability_log_dir"]}/glances_{localtime}.csv'
#         log_files_dict['logfile_with_path'] = f'{log_files_dict["stability_log_dir"]}/stability_{localtime}.log'
#         log_files_dict['loghtml_with_path'] = f'{log_files_dict["stability_log_dir"]}/stability_{localtime}.log.html'
#         log_files_dict['final_html_with_path'] = f'{log_files_dict["stability_log_dir"]}/stability_{localtime}.html'
#         log_files_dict['linehtml'] = f"pyecharts-line_{localtime}.html"
#         log_files_dict['baseDataBarhtml'] = f"pyecharts-baseDataBar{localtime}.html"
#         log_files_dict['statusPie_html'] = f"pyecharts-statusPie_{localtime}.html"
#         log_files_dict['loghtml'] = f'stability_{localtime}.log.html'
#         log_files_dict[
#             'glance_html_with_path'] = f'{log_files_dict["stability_log_dir"]}/pyecharts-glance_{localtime}.html'
#         log_files_dict[
#             'glance_io_html_with_path'] = f'{log_files_dict["stability_log_dir"]}/pyecharts-glance-io_{localtime}.html'
#         log_files_dict[
#             'baseDataBar_html_with_path'] = f'{log_files_dict["stability_log_dir"]}/pyecharts-baseDataBar_{localtime}.html'
#         log_files_dict[
#             'baseGslbDataBar_html_with_path'] = f'{log_files_dict["stability_log_dir"]}/pyecharts-baseGslbDataBar_{localtime}.html'
#         log_files_dict[
#             'errorLogCountBar_html_with_path'] = f'{log_files_dict["stability_log_dir"]}/pyecharts-errorLogCountBar_{localtime}.html'
#         log_files_dict[
#             'statusPie_html_with_path'] = f'{log_files_dict["stability_log_dir"]}/pyecharts-statusPie_{localtime}.html'
#         log_files_dict['dnsperf_log'] = f'dnsperf_{localtime}.log'
#         log_files_dict['slaveDnsperf_log'] = f'slaveDnsperf_{localtime}.log'
#         log_files_dict['dnsperf_log_with_path'] = f'/tmp/dnsperf_{localtime}.log'
#         log_files_dict['dnsperf_csv_with_path'] = f'{log_files_dict["stability_log_dir"]}/dnsperf_{localtime}.csv'
#         log_files_dict['dnsperf_html_with_path'] = f'{log_files_dict["stability_log_dir"]}/dnsperf_{localtime}.html'
#         log_files_dict[
#             'resolutionSuccessRate_csv_with_path'] = f'{log_files_dict["stability_log_dir"]}/resolutionSuccessRate_{localtime}.csv'
#         log_files_dict[
#             'resolutionSuccessRate_html_with_path'] = f'{log_files_dict["stability_log_dir"]}/resolutionSuccessRate_{localtime}.html'
#         log_files_dict['report_html_with_path'] = f'{log_files_dict["stability_log_dir"]}/report_{localtime}.html'
#         return log_files_dict, localtime
#
#     def genMonitorLogFiles(self, roll, localtime):
#         log_files_dict = {}
#         log_files_dict['localtime'] = localtime
#         log_files_dict['stability_log_dir'] = f'{log_dir}/stability_{localtime}'
#         log_files_dict['glancecsv_filename'] = f'{roll}_glances_{localtime}.csv'
#         log_files_dict['remote_glancecsv_filename_with_path'] = f'/tmp/{roll}_glances_{localtime}.csv'
#         log_files_dict[
#             'local_glancecsv_filename_with_path'] = f'{log_files_dict["stability_log_dir"]}/{roll}_glances_{localtime}.csv'
#         log_files_dict['logfile_with_path'] = f'{log_files_dict["stability_log_dir"]}/{roll}_stability_{localtime}.log'
#         log_files_dict[
#             'loghtml_with_path'] = f'{log_files_dict["stability_log_dir"]}/{roll}_stability_{localtime}.log.html'
#         log_files_dict[
#             'final_html_with_path'] = f'{log_files_dict["stability_log_dir"]}/{roll}_stability_{localtime}.html'
#         log_files_dict['linehtml'] = f"{roll}_pyecharts-line_{localtime}.html"
#         log_files_dict['baseDataBarhtml'] = f"{roll}_pyecharts-baseDataBar{localtime}.html"
#         log_files_dict['statusPie_html'] = f"{roll}_pyecharts-statusPie_{localtime}.html"
#         log_files_dict['loghtml'] = f'{roll}_stability_{localtime}.log.html'
#         log_files_dict[
#             'glance_html_with_path'] = f'{log_files_dict["stability_log_dir"]}/{roll}_pyecharts-glance_{localtime}.html'
#         log_files_dict[
#             'glance_io_html_with_path'] = f'{log_files_dict["stability_log_dir"]}/{roll}_pyecharts-glance-io_{localtime}.html'
#         log_files_dict[
#             'baseDataBar_html_with_path'] = f'{log_files_dict["stability_log_dir"]}/{roll}_pyecharts-baseDataBar_{localtime}.html'
#         log_files_dict[
#             'baseGslbDataBar_html_with_path'] = f'{log_files_dict["stability_log_dir"]}/{roll}_pyecharts-baseGslbDataBar_{localtime}.html'
#         log_files_dict[
#             'errorLogCountBar_html_with_path'] = f'{log_files_dict["stability_log_dir"]}/{roll}_pyecharts-errorLogCountBar_{localtime}.html'
#         log_files_dict[
#             'statusPie_html_with_path'] = f'{log_files_dict["stability_log_dir"]}/{roll}_pyecharts-statusPie_{localtime}.html'
#         log_files_dict['dnsperf_log'] = f'{roll}_dnsperf_{localtime}.log'
#         log_files_dict['dnsperf_log_with_path'] = f'/tmp/{roll}_dnsperf_{localtime}.log'
#         log_files_dict[
#             'dnsperf_csv_with_path'] = f'{log_files_dict["stability_log_dir"]}/{roll}_dnsperf_{localtime}.csv'
#         log_files_dict[
#             'dnsperf_html_with_path'] = f'{log_files_dict["stability_log_dir"]}/{roll}_dnsperf_{localtime}.html'
#         log_files_dict[
#             'resolutionSuccessRate_csv_with_path'] = f'{log_files_dict["stability_log_dir"]}/{roll}_resolutionSuccessRate_{localtime}.csv'
#         log_files_dict[
#             'resolutionSuccessRate_html_with_path'] = f'{log_files_dict["stability_log_dir"]}/{roll}_resolutionSuccessRate_{localtime}.html'
#         log_files_dict[
#             'report_html_with_path'] = f'{log_files_dict["stability_log_dir"]}/{roll}_report_{localtime}.html'
#         return log_files_dict
#
#     def transHtml(self, logfile_with_path):
#         contents = open(logfile_with_path, "r")
#         with open(f"{logfile_with_path}.html", "w") as e:
#             for lines in contents.readlines():
#                 e.write("<pre>" + lines + "</pre> <br>\n")
#
#     #         time.sleep(5)
#     #         if os.path.exists(logfile_with_path):
#     #             os.remove(logfile_with_path)
#
#     def unionHtml(self, final_html_with_path, firstHtml, *appendHtml):
#         with open(final_html_with_path, "w") as e:
#             e.write(
#                 f'<iframe name="iframe1" marginwidth=0 marginheight=0 width=100% height="600" src="{firstHtml}" frameborder=0></iframe>')
#             for html in appendHtml:
#                 e.write(
#                     f'<iframe name="iframe1" marginwidth=0 marginheight=0 width=100% height="600" src="{html}" frameborder=0></iframe>')
#
#     def unionReport(self, report_html_with_path, htmls):
#         head_write = """
# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Document</title>
# </head>
# <body>
# """
#         end_write = """
# </body>
# </html>
# """
#         with open(report_html_with_path, "w") as e:
#             e.write(head_write)
#             for html in htmls:
#                 e.write("<div>")
#                 with open(html, "r") as fp:
#                     contents = fp.read()
#                     e.write(contents)
#                 e.write("</div>")
#             e.write(end_write)
#
#     #    def putPyechartsJson(self):
#     #        if "windows" in platform.system().lower():
#     #            json_path = 'C:\\pyecharts'
#     #        else:
#     #            json_path = '/tmp/pyecharts'
#     #        if os.path.exists(json_path) is False:
#     #            shutil.copytree(f'{upload_path}/pyecharts', json_path)
#     #            logger.success('json_path copy success')
#     #        return json_path
#
#     def installPython(self):
#         if auto_install.lower() == "true":
#             pass
#             # if "windows" in platform.system().lower():
#             #     logger.info(
#             #         "!!! Detect your system is windows, you need install python3 version>3.6 and pip3 libs by yourself")
#             # else:
#             #     if "el7" in Util.exec_shell_cmd('uname -r') and "x86" in Util.exec_shell_cmd('uname -r'):
#             #         self.exec_shell_cmd(
#             #             'grep "^nameserver 8.8.8.8" /etc/resolv.conf >> /dev/null ;if [ $? -ne 0 ];then echo -e "" >> /etc/resolv.conf && sed -i "1i nameserver 8.8.8.8" /etc/resolv.conf; fi && yum install -y python3 python3-devel gcc gcc-c++ libxml2 libxslt libxml2-devel libxslt-devel libffi-devel screen &&  python3 -m pip install --upgrade pip && pip3 install setuptools_rust requests numpy pandas pyecharts yagmail fabric clientsubnetoption loguru configparser APScheduler -i http://mirrors.aliyun.com/pypi/simple/  --trusted-host mirrors.aliyun.com')
#             #     elif "el6" in Util.exec_shell_cmd('uname -r') and "x86" in Util.exec_shell_cmd('uname -r'):
#             #         self.exec_shell_cmd('you need install python3 version>3.6 and pip3 libs by yourself')
#             #     elif "el7" in Util.exec_shell_cmd('uname -r') and "aarch64" in Util.exec_shell_cmd('uname -r'):
#             #         self.exec_shell_cmd(
#             #             'grep "^nameserver 8.8.8.8" /etc/resolv.conf >> /dev/null ;if [ $? -ne 0 ];then echo -e "" >> /etc/resolv.conf && sed -i "1i nameserver 8.8.8.8" /etc/resolv.conf; fi && yum install -y python3 python3-devel gcc gcc-c++ libxml2 libxslt libxml2-devel libxslt-devel libffi-devel screen &&  python3 -m pip install --upgrade pip && pip3 install setuptools_rust requests numpy pandas pyecharts yagmail fabric clientsubnetoption loguru configparser APScheduler -i http://mirrors.aliyun.com/pypi/simple/  --trusted-host mirrors.aliyun.com')
#             #     elif "ky10" in Util.exec_shell_cmd('uname -r') and "aarch64" in Util.exec_shell_cmd('uname -r'):
#             #         self.exec_shell_cmd(
#             #             'grep "^nameserver 8.8.8.8" /etc/resolv.conf >> /dev/null ;if [ $? -ne 0 ];then echo -e "" >> /etc/resolv.conf && sed -i "1i nameserver 8.8.8.8" /etc/resolv.conf; fi && yum install -y python3 python3-devel python3-pip gcc gcc-c++ libxml2 libxslt libxml2-devel libxslt-devel libffi-devel screen &&  python3 -m pip install --upgrade pip && pip3 install setuptools_rust requests numpy pandas pyecharts yagmail fabric clientsubnetoption loguru configparser APScheduler -i http://mirrors.aliyun.com/pypi/simple/  --trusted-host mirrors.aliyun.com')
#         else:
#             logger.warning(
#                 "!!! Your conf file has set auto_install to False, please install python3 and libs by manual")
#
#     def installMasterenv(self):
#         if self.getSystemEnv()[0] == "CENTOS7" or self.getSystemEnv()[0] == "KYLIN10":
#             self.RM_master.exec_cmd(
#                 'grep "^nameserver 8.8.8.8" /etc/resolv.conf >> /dev/null ;if [ $? -ne 0 ];then echo -e "" >> /etc/resolv.conf && sed -i "1i nameserver 8.8.8.8" /etc/resolv.conf; fi && yum install -y python3 python3-devel python3-pip screen && pip3 install glances -i http://mirrors.aliyun.com/pypi/simple/  --trusted-host mirrors.aliyun.com')
#         else:
#             self.RM_master.upload_file("Python-3.6.5-n.el6.x86_64.rpm", remote_dir)
#             self.RM_master.upload_file("screen-4.0.3-16.el6.x86_64.rpm", remote_dir)
#             self.RM_master.exec_cmd(
#                 'grep "^nameserver 8.8.8.8" /etc/resolv.conf >> /dev/null ;if [ $? -ne 0 ];then echo -e "" >> /etc/resolv.conf && sed -i "1i nameserver 8.8.8.8" /etc/resolv.conf; fi && cd /root && rpm -ivh Python-3.6.5-n.el6.x86_64.rpm screen-4.0.3-16.el6.x86_64.rpm --force --nodeps && pip3 install glances -i http://mirrors.aliyun.com/pypi/simple/  --trusted-host mirrors.aliyun.com')
#         glances_path = self.RM_master.exec_cmd('find / -name glances 2>&1 | grep bin | grep -v "/usr/bin/glances"')
#         handle_glances_path = glances_path.replace('\n', '')
#         self.RM_master.exec_cmd(f'ln -sf {handle_glances_path} /usr/bin/glances > /dev/null')
#         glances_version = self.RM_master.exec_cmd('glances --version')
#         if "glances v" in str(glances_version).lower():
#             logger.info("-------------glances install ok---------------")
#             return "glances install ok", 200
#         else:
#             logger.error(f"-------------glances install failed---------------")
#             return "glances install failed", 500
#
#     def installMonitorEnv(self, roll):
#         '''
#             roll must be monitor1, monitor2 or monitor3
#         '''
#         if roll == "monitor1":
#             sys_info = self.getSystemEnv(roll=roll)
#             if sys_info == "CENTOS7" or sys_info == "KYLIN10":
#                 self.RM_monitor1.exec_cmd(
#                     'grep "^nameserver 8.8.8.8" /etc/resolv.conf >> /dev/null ;if [ $? -ne 0 ];then echo -e "" >> /etc/resolv.conf && sed -i "1i nameserver 8.8.8.8" /etc/resolv.conf; fi && yum install -y python3 python3-devel python3-pip screen && pip3 install glances -i http://mirrors.aliyun.com/pypi/simple/  --trusted-host mirrors.aliyun.com')
#             else:
#                 self.RM_monitor1.upload_file("Python-3.6.5-n.el6.x86_64.rpm", remote_dir)
#                 self.RM_monitor1.upload_file("screen-4.0.3-16.el6.x86_64.rpm", remote_dir)
#                 self.RM_monitor1.exec_cmd(
#                     'grep "^nameserver 8.8.8.8" /etc/resolv.conf >> /dev/null ;if [ $? -ne 0 ];then echo -e "" >> /etc/resolv.conf && sed -i "1i nameserver 8.8.8.8" /etc/resolv.conf; fi && cd /root && rpm -ivh Python-3.6.5-n.el6.x86_64.rpm screen-4.0.3-16.el6.x86_64.rpm --force --nodeps && pip3 install glances -i http://mirrors.aliyun.com/pypi/simple/  --trusted-host mirrors.aliyun.com')
#             glances_path = self.RM_monitor1.exec_cmd(
#                 'find / -name glances 2>&1 | grep bin | grep -v "/usr/bin/glances"')
#             handle_glances_path = glances_path.replace('\n', '')
#             self.RM_monitor1.exec_cmd(f'ln -sf {handle_glances_path} /usr/bin/glances > /dev/null')
#             glances_version = self.RM_monitor1.exec_cmd('glances --version')
#             if "glances v" in str(glances_version).lower():
#                 logger.info(f"-------------{monitor1_name} glances install ok---------------")
#                 return f"{monitor1_name} glances install ok", 200
#             else:
#                 logger.error(f"-------------{monitor1_name} glances install failed---------------")
#                 return f"{monitor1_name} glances install failed", 500
#         elif roll == "monitor2":
#             sys_info = self.getSystemEnv(roll=roll)
#             if sys_info == "CENTOS7" or sys_info == "KYLIN10":
#                 self.RM_monitor2.exec_cmd(
#                     'grep "^nameserver 8.8.8.8" /etc/resolv.conf >> /dev/null ;if [ $? -ne 0 ];then echo -e "" >> /etc/resolv.conf && sed -i "1i nameserver 8.8.8.8" /etc/resolv.conf; fi && yum install -y python3 python3-devel python3-pip screen && pip3 install glances -i http://mirrors.aliyun.com/pypi/simple/  --trusted-host mirrors.aliyun.com')
#             else:
#                 self.RM_monitor2.upload_file("Python-3.6.5-n.el6.x86_64.rpm", remote_dir)
#                 self.RM_monitor2.upload_file("screen-4.0.3-16.el6.x86_64.rpm", remote_dir)
#                 self.RM_monitor2.exec_cmd(
#                     'grep "^nameserver 8.8.8.8" /etc/resolv.conf >> /dev/null ;if [ $? -ne 0 ];then echo -e "" >> /etc/resolv.conf && sed -i "1i nameserver 8.8.8.8" /etc/resolv.conf; fi && cd /root && rpm -ivh Python-3.6.5-n.el6.x86_64.rpm screen-4.0.3-16.el6.x86_64.rpm --force --nodeps && pip3 install glances -i http://mirrors.aliyun.com/pypi/simple/  --trusted-host mirrors.aliyun.com')
#             glances_path = self.RM_monitor2.exec_cmd(
#                 'find / -name glances 2>&1 | grep bin | grep -v "/usr/bin/glances"')
#             handle_glances_path = glances_path.replace('\n', '')
#             self.RM_monitor2.exec_cmd(f'ln -sf {handle_glances_path} /usr/bin/glances > /dev/null')
#             glances_version = self.RM_monitor2.exec_cmd('glances --version')
#             if "glances v" in str(glances_version).lower():
#                 logger.info(f"-------------{monitor2_name} glances install ok---------------")
#                 return f"{monitor2_name} glances install ok", 200
#             else:
#                 logger.error(f"-------------{monitor2_name} glances install failed---------------")
#                 return f"{monitor2_name} glances install failed", 500
#         elif roll == "monitor3":
#             sys_info = self.getSystemEnv(roll=roll)
#             if sys_info == "CENTOS7" or sys_info == "KYLIN10":
#                 self.RM_monitor3.exec_cmd(
#                     'grep "^nameserver 8.8.8.8" /etc/resolv.conf >> /dev/null ;if [ $? -ne 0 ];then echo -e "" >> /etc/resolv.conf && sed -i "1i nameserver 8.8.8.8" /etc/resolv.conf; fi && yum install -y python3 python3-devel python3-pip screen && pip3 install glances -i http://mirrors.aliyun.com/pypi/simple/  --trusted-host mirrors.aliyun.com')
#             else:
#                 self.RM_monitor3.upload_file("Python-3.6.5-n.el6.x86_64.rpm", remote_dir)
#                 self.RM_monitor3.upload_file("screen-4.0.3-16.el6.x86_64.rpm", remote_dir)
#                 self.RM_monitor3.exec_cmd(
#                     'grep "^nameserver 8.8.8.8" /etc/resolv.conf >> /dev/null ;if [ $? -ne 0 ];then echo -e "" >> /etc/resolv.conf && sed -i "1i nameserver 8.8.8.8" /etc/resolv.conf; fi && cd /root && rpm -ivh Python-3.6.5-n.el6.x86_64.rpm screen-4.0.3-16.el6.x86_64.rpm --force --nodeps && pip3 install glances -i http://mirrors.aliyun.com/pypi/simple/  --trusted-host mirrors.aliyun.com')
#             glances_path = self.RM_monitor3.exec_cmd(
#                 'find / -name glances 2>&1 | grep bin | grep -v "/usr/bin/glances"')
#             handle_glances_path = glances_path.replace('\n', '')
#             self.RM_monitor3.exec_cmd(f'ln -sf {handle_glances_path} /usr/bin/glances > /dev/null')
#             glances_version = self.RM_monitor3.exec_cmd('glances --version')
#             if "glances v" in str(glances_version).lower():
#                 logger.info(f"-------------{monitor3_name} glances install ok---------------")
#                 return f"{monitor3_name} glances install ok", 200
#             else:
#                 logger.error(f"-------------{monitor3_name} glances install failed---------------")
#                 return f"{monitor3_name} glances install failed", 500
#
#     def installClientenv(self):
#         if self.getSystemEnv()[1] == "CENTOS7" or self.getSystemEnv()[1] == "KYLIN10":
#             self.RM_client.exec_cmd(
#                 'rm -rf /root/dnsperf*; grep "^nameserver 8.8.8.8" /etc/resolv.conf >> /dev/null ;if [ $? -ne 0 ];then echo -e "" >> /etc/resolv.conf && sed -i "1i nameserver 8.8.8.8" /etc/resolv.conf; fi && yum install -y bind-utils screen')
#         else:
#             self.RM_client.upload_file("bind-utils-9.8.2-0.17.rc1.el6.x86_64.rpm", remote_dir)
#             self.RM_client.upload_file("screen-4.0.3-16.el6.x86_64.rpm", remote_dir)
#             self.RM_client.exec_cmd(
#                 'rm -rf /root/dnsperf*; grep "^nameserver 8.8.8.8" /etc/resolv.conf >> /dev/null ;if [ $? -ne 0 ];then echo -e "" >> /etc/resolv.conf && sed -i "1i nameserver 8.8.8.8" /etc/resolv.conf; fi && cd /root && rpm -ivh bind-utils-9.8.2-0.17.rc1.el6.x86_64.rpm screen-4.0.3-16.el6.x86_64.rpm --force --nodeps')
#         self.RM_client.exec_cmd(
#             'grep "^logfile" /etc/screenrc >> /dev/null;if [ $? -ne 0 ];then echo -e "logfile /tmp/%t" >> /etc/screenrc;fi')
#         kernel_info = self.RM_client.exec_cmd('uname -r')
#         if "aarch" in str(kernel_info):
#             dnsperf_file = 'dnsperf_arm'
#         else:
#             dnsperf_file = 'dnsperf'
#         self.RM_client.upload_file(dnsperf_file, remote_dnsperf)
#         self.RM_client.upload_file(qpdata_local, remote_dir)
#         self.RM_client.exec_cmd('chmod +x /root/dnsperf')
#         if Dns_Flag.lower() != "true":
#             self.RM_client.exec_cmd('mv -f /root/dnsperf_gslb_only.txt /root/dnsperf.txt')
#         dnsperf_version = self.RM_client.exec_cmd('/root/dnsperf -h')
#         if "version" in str(dnsperf_version).lower():
#             logger.info("-------------dnsperf install ok---------------")
#             return 'dnsperf install ok', 200
#         else:
#             logger.error(f"-------------dnsperf install failed-------------")
#             return "dnsperf install failed", 500
#
#     def drawBaseDataBars(self, baseDataBar_html_with_path, keylist=[], success_valuelist=[], fail_valuelist=[]):
#         bar = (
#             Bar(init_opts=opts.InitOpts(width="1300px", height="600px"))
#                 .add_xaxis(keylist)
#                 .add_yaxis("成功", success_valuelist, category_gap='50%', color="#00FF00")
#                 .add_yaxis("失败", fail_valuelist, category_gap='50%')
#                 .set_global_opts(title_opts=opts.TitleOpts(title="DNS基础数据"))
#         )
#         bar.render(baseDataBar_html_with_path)
#
#     def drawBaseGslbDataBars(self, baseGslbDataBar_html_with_path, keylist=[], success_valuelist=[], fail_valuelist=[]):
#         bar = (
#             Bar(init_opts=opts.InitOpts(width="1300px", height="600px"))
#                 .add_xaxis(keylist)
#                 .add_yaxis("成功", success_valuelist, category_gap='50%', color="#00FF00")
#                 .add_yaxis("失败", fail_valuelist, category_gap='50%')
#                 .set_global_opts(title_opts=opts.TitleOpts(title="GSLB基础数据"))
#         )
#         bar.render(baseGslbDataBar_html_with_path)
#
#     def drawErrorLogCountBars(self, errorLogCountBar_html_with_path, start_time, end_time, roll):
#         keylist = self.getLogErrorCount()[0]
#         error_count_list = self.getLogErrorCount()[1]
#         keylist.append("alarm.db")
#         error_count_list.append(self.getAlarmDbCount(start_time, end_time))
#         error_count_list = list(map(int, error_count_list))
#         if roll == "master":
#             title = 'master日志ERROR数量'
#         elif roll == "monitor1":
#             title = f'{monitor1_name}日志ERROR数量'
#         elif roll == "monitor2":
#             title = f'{monitor2_name}日志ERROR数量'
#         elif roll == "monitor3":
#             title = f'{monitor3_name}日志ERROR数量'
#         bar = (
#             Bar(init_opts=opts.InitOpts(width="1300px", height="600px"))
#                 .add_xaxis(keylist)
#                 .add_yaxis("ERROR COUNT", error_count_list, category_gap='70%')
#                 .set_global_opts(title_opts=opts.TitleOpts(title=title),
#                                  datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")])
#         )
#         bar.render(errorLogCountBar_html_with_path)
#
#     def runGlances(self, remote_glancecsv_filename_with_path, monitor1_log_files_dict, monitor2_log_files_dict,
#                    monitor3_log_files_dict):
#         try:
#             self.RM_master.exec_cmd(
#                 'ps -ef | grep glances | grep -v grep | awk \'{print $2}\' | xargs kill -9;' + f'screen -d -m glances -t 720 --stdout-csv now,cpu.user,mem.used,load --export csv --export-csv-file {remote_glancecsv_filename_with_path} --export-csv-overwrite')
#             if monitor1.lower() == "true":
#                 self.runMonitorGlances("monitor1", monitor1_log_files_dict['remote_glancecsv_filename_with_path'])
#             if monitor2.lower() == "true":
#                 self.runMonitorGlances("monitor2", monitor2_log_files_dict['remote_glancecsv_filename_with_path'])
#             if monitor3.lower() == "true":
#                 self.runMonitorGlances("monitor3", monitor3_log_files_dict['remote_glancecsv_filename_with_path'])
#         except Exception as e:
#             logger.error(f'run glances error --- {e}')
#
#     def runMonitorGlances(self, roll, monitor_remote_glancecsv_filename_with_path):
#         try:
#             if roll == "monitor1":
#                 self.RM_monitor1.exec_cmd(
#                     'ps -ef | grep glances | grep -v grep | awk \'{print $2}\' | xargs kill -9;' + f'screen -d -m glances -t 720 --stdout-csv now,cpu.user,mem.used,load --export csv --export-csv-file {monitor_remote_glancecsv_filename_with_path} --export-csv-overwrite')
#             if roll == "monitor2":
#                 self.RM_monitor2.exec_cmd(
#                     'ps -ef | grep glances | grep -v grep | awk \'{print $2}\' | xargs kill -9;' + f'screen -d -m glances -t 720 --stdout-csv now,cpu.user,mem.used,load --export csv --export-csv-file {monitor_remote_glancecsv_filename_with_path} --export-csv-overwrite')
#             if roll == "monitor3":
#                 self.RM_monitor3.exec_cmd(
#                     'ps -ef | grep glances | grep -v grep | awk \'{print $2}\' | xargs kill -9;' + f'screen -d -m glances -t 720 --stdout-csv now,cpu.user,mem.used,load --export csv --export-csv-file {monitor_remote_glancecsv_filename_with_path} --export-csv-overwrite')
#         except Exception as e:
#             logger.error(f'run {roll} glances error --- {e}')
#
#     def getGlancecsv(self, log_files_dict, monitor1_log_files_dict, monitor2_log_files_dict, monitor3_log_files_dict):
#         try:
#             self.RM_master.download_file(log_files_dict['remote_glancecsv_filename_with_path'],
#                                          log_files_dict['local_glancecsv_filename_with_path'])
#             if monitor1.lower() == "true":
#                 self.getMonitorGlancecsv("monitor1", monitor1_log_files_dict['remote_glancecsv_filename_with_path'],
#                                          monitor1_log_files_dict['local_glancecsv_filename_with_path'])
#             if monitor2.lower() == "true":
#                 self.getMonitorGlancecsv("monitor2", monitor2_log_files_dict['remote_glancecsv_filename_with_path'],
#                                          monitor2_log_files_dict['local_glancecsv_filename_with_path'])
#             if monitor3.lower() == "true":
#                 self.getMonitorGlancecsv("monitor3", monitor3_log_files_dict['remote_glancecsv_filename_with_path'],
#                                          monitor3_log_files_dict['local_glancecsv_filename_with_path'])
#         except Exception as e:
#             logger.error(f'getGlancecsv error --- {e}')
#
#     def getMonitorGlancecsv(self, roll, remote_glancecsv_filename_with_path, local_glancecsv_filename_with_path):
#         try:
#             if roll == "monitor1":
#                 self.RM_monitor1.download_file(remote_glancecsv_filename_with_path, local_glancecsv_filename_with_path)
#             if roll == "monitor2":
#                 self.RM_monitor2.download_file(remote_glancecsv_filename_with_path, local_glancecsv_filename_with_path)
#             if roll == "monitor3":
#                 self.RM_monitor3.download_file(remote_glancecsv_filename_with_path, local_glancecsv_filename_with_path)
#         except Exception as e:
#             logger.error(f'{roll} getGlancecsv error --- {e}')
#
#     def getDiskType(self):
#         try:
#             disk_type_result = self.RM_master.exec_cmd("fdisk -l")
#             if "/dev/sda" in disk_type_result:
#                 return "sda"
#             elif "/dev/vda" in disk_type_result:
#                 return "vda"
#         except Exception as e:
#             logger.error(f'getDiskType error --- {e}')
#
#     def drawSystemLines(self, roll, log_files_dict):
#         data = pd.DataFrame(
#             pd.read_csv(log_files_dict['local_glancecsv_filename_with_path'], header=0, encoding="utf-8").drop(
#                 index=[0]))
#         timestamp = np.array(data['timestamp'])
#         cpu_percent = np.array(data['cpu_total'])
#         mem_percent = np.array(data['mem_percent'])
#         fs_percent = np.array(data['fs_/_percent'])
#         if roll == "master":
#             title = 'master资源使用率'
#         elif roll == "monitor1":
#             title = f'{monitor1_name}资源使用率'
#         elif roll == "monitor2":
#             title = f'{monitor2_name}资源使用率'
#         elif roll == "monitor3":
#             title = f'{monitor3_name}资源使用率'
#         line1 = (
#             Line(init_opts=opts.InitOpts(width="1300px", height="500px"))
#                 .add_xaxis(xaxis_data=list(timestamp))
#                 .add_yaxis(series_name='cpu_percent', y_axis=list(cpu_percent), is_smooth=True)
#                 .add_yaxis(series_name='mem_percent', y_axis=list(mem_percent), is_smooth=True)
#                 .add_yaxis(series_name='fs_percent', y_axis=list(fs_percent), is_smooth=True)
#                 .set_global_opts(title_opts=opts.TitleOpts(title=title),
#                                  tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"))
#                 .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
#         )
#         line1.render(log_files_dict['glance_html_with_path'])
#
#     def drawSystemIoLines(self, roll, log_files_dict):
#         if self.getDiskType() == "sda":
#             diskio_read_count = "diskio_sda_read_count"
#             diskio_write_count = "diskio_sda_write_count"
#         elif self.getDiskType() == "vda":
#             diskio_read_count = "diskio_vda_read_count"
#             diskio_write_count = "diskio_vda_write_count"
#         data = pd.DataFrame(
#             pd.read_csv(log_files_dict['local_glancecsv_filename_with_path'], header=0, encoding="utf-8").drop(
#                 index=[0]))
#         timestamp = np.array(data['timestamp'])
#         timestamp_list = list(timestamp)
#         if len(timestamp_list) > 0:
#             timestamp_list.pop(0)
#         diskio_vsda_read_count = np.array(data[diskio_read_count])
#         diskio_vsda_write_count = np.array(data[diskio_write_count])
#         read_count_list = list(map(int, diskio_vsda_read_count))
#         if len(read_count_list) > 0:
#             read_count_list.pop(0)
#         write_count_list = list(map(int, diskio_vsda_write_count))
#         if len(write_count_list) > 0:
#             write_count_list.pop(0)
#         if roll == "master":
#             title = 'master磁盘IO'
#         elif roll == "monitor1":
#             title = f'{monitor1_name}磁盘IO'
#         elif roll == "monitor2":
#             title = f'{monitor2_name}磁盘IO'
#         elif roll == "monitor3":
#             title = f'{monitor3_name}磁盘IO'
#         line1 = (
#             Line(init_opts=opts.InitOpts(width="1300px", height="500px"))
#                 .add_xaxis(xaxis_data=timestamp_list)
#                 .add_yaxis(series_name=diskio_read_count, y_axis=read_count_list, is_smooth=True)
#                 .add_yaxis(series_name=diskio_write_count, y_axis=write_count_list, is_smooth=True)
#                 .set_global_opts(title_opts=opts.TitleOpts(title=title),
#                                  tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"))
#                 .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
#         )
#         line1.render(log_files_dict['glance_io_html_with_path'])
#
#     def genDnsperfCmd(self, dnsperf_log, runtime_update):
#         cmd = 'ps -ef | grep dnsperf | grep %s | grep -v grep | awk \'{print $2}\' | xargs kill -9;' % (
#             master_ip) + f'screen -d -m -L -t {dnsperf_log} /root/dnsperf -s {master_ip} -p {master_query_port} -c {client_count} -d {qpdata_client} -t {time_out} -l {runtime_update} -q {max_num_qps} -Q {qps_limit} -S {print_qps}'
#         return cmd
#
#     def genSlaveDnsperfCmd(self, dnsperf_log, runtime_update):
#         cmd = 'ps -ef | grep dnsperf | grep %s | grep -v grep | awk \'{print $2}\' | xargs kill -9;' % (
#             slave_ip) + f'screen -d -m -L -t {dnsperf_log} /root/dnsperf -s {slave_ip} -p {slave_query_port} -c {client_count} -d {qpdata_client} -t {time_out} -l {runtime_update} -q {max_num_qps} -Q {slave_qps_limit} -S {print_qps}'
#         return cmd
#
#     def genSlave2DnsperfCmd(self, dnsperf_log, runtime_update):
#         cmd = 'ps -ef | grep dnsperf | grep %s | grep -v grep | awk \'{print $2}\' | xargs kill -9;' % (
#             slave2_ip) + f'screen -d -m -L -t {dnsperf_log} /root/dnsperf -s {slave2_ip} -p {slave2_query_port} -c {client_count} -d {qpdata_client} -t {time_out} -l {runtime_update} -q {max_num_qps} -Q {slave2_qps_limit} -S {print_qps}'
#         return cmd
#
#     def genMonitor1DnsperfCmd(self, dnsperf_log, runtime_update):
#         cmd = 'ps -ef | grep dnsperf | grep %s | grep -v grep | awk \'{print $2}\' | xargs kill -9;' % (
#             monitor1_ip) + f'screen -d -m -L -t {dnsperf_log} /root/dnsperf -s {monitor1_ip} -p {monitor1_query_port} -c {client_count} -d {qpdata_client} -t {time_out} -l {runtime_update} -q {max_num_qps} -Q {monitor1_qps_limit} -S {print_qps}'
#         return cmd
#
#     def genMonitor2DnsperfCmd(self, dnsperf_log, runtime_update):
#         cmd = 'ps -ef | grep dnsperf | grep %s | grep -v grep | awk \'{print $2}\' | xargs kill -9;' % (
#             monitor2_ip) + f'screen -d -m -L -t {dnsperf_log} /root/dnsperf -s {monitor2_ip} -p {monitor2_query_port} -c {client_count} -d {qpdata_client} -t {time_out} -l {runtime_update} -q {max_num_qps} -Q {monitor2_qps_limit} -S {print_qps}'
#         return cmd
#
#     def genMonitor3DnsperfCmd(self, dnsperf_log, runtime_update):
#         cmd = 'ps -ef | grep dnsperf | grep %s | grep -v grep | awk \'{print $2}\' | xargs kill -9;' % (
#             monitor3_ip) + f'screen -d -m -L -t {dnsperf_log} /root/dnsperf -s {monitor3_ip} -p {monitor3_query_port} -c {client_count} -d {qpdata_client} -t {time_out} -l {runtime_update} -q {max_num_qps} -Q {monitor3_qps_limit} -S {print_qps}'
#         return cmd
#
#     def runDnsperf(self, log_files_dict, monitor1_log_files_dict, monitor2_log_files_dict, monitor3_log_files_dict,
#                    runtime_update):
#         try:
#             self.RM_client.exec_cmd(self.genDnsperfCmd(log_files_dict['dnsperf_log'], runtime_update))
#             if slave.lower() == "true":
#                 self.RM_client.exec_cmd(self.genSlaveDnsperfCmd(log_files_dict['slaveDnsperf_log'], runtime_update))
#             if slave2.lower() == "true":
#                 self.RM_client.exec_cmd(self.genSlave2DnsperfCmd(log_files_dict['slaveDnsperf_log'], runtime_update))
#             if monitor1.lower() == "true":
#                 self.RM_monitor1.exec_cmd(
#                     self.genMonitor1DnsperfCmd(monitor1_log_files_dict['dnsperf_log'], runtime_update))
#             if monitor2.lower() == "true":
#                 self.RM_monitor2.exec_cmd(
#                     self.genMonitor2DnsperfCmd(monitor2_log_files_dict['dnsperf_log'], runtime_update))
#             if monitor3.lower() == "true":
#                 self.RM_monitor3.exec_cmd(
#                     self.genMonitor3DnsperfCmd(monitor3_log_files_dict['dnsperf_log'], runtime_update))
#         except Exception as e:
#             logger.error(f'run dnsperf error --- {e}')
#
#     def getFinalDnsperfData(self, log_files_dict):
#         datatime = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(time.time()))
#         dnsperfData = self.RM_client.exec_cmd(
#             f'sed -i "/Timeout/d" {log_files_dict["dnsperf_log_with_path"]};sed -i "/Warning/d" {log_files_dict["dnsperf_log_with_path"]}; tail -1 {log_files_dict["dnsperf_log_with_path"]}')
#         if ":" in str(dnsperfData):
#             finalDnsperfData = str(dnsperfData).split(':')[1].split('.')[0].replace(" ", "").replace('\n', "")
#             if self.is_number(finalDnsperfData):
#                 return [datatime, int(finalDnsperfData)]
#             else:
#                 return [datatime, 0]
#         else:
#             return [datatime, 0]
#
#     def writeDnsperfDataToCsv(self, dnsperf_csv_with_path, datalist):
#         if os.path.exists(dnsperf_csv_with_path) is False:
#             fd = open(dnsperf_csv_with_path, mode="w", encoding="utf-8")
#             fd.close()
#         with open(dnsperf_csv_with_path, "r", encoding='utf-8', newline="") as e:
#             lines = e.readlines()
#         with open(dnsperf_csv_with_path, "a+", encoding='utf-8', newline="") as e:
#             csv_writer = csv.writer(e)
#             if str(datalist[1]) not in str(lines) and datalist[1] != 0:
#                 csv_writer.writerow(datalist)
#
#     def drawDnsperfDataLine(self, roll, log_files_dict):
#         datatime_list = []
#         dnsperfdata_list = []
#         with open(log_files_dict['dnsperf_csv_with_path'], 'r') as csvfile:
#             reader = csv.reader(csvfile)
#             for row in reader:
#                 datatime_list.append(row[0])
#                 dnsperfdata_list.append(row[1])
#         if roll == "master":
#             title = 'master_dnsperf数据'
#         elif roll == "monitor1":
#             title = f'{monitor1_name}_dnsperf数据'
#         elif roll == "monitor2":
#             title = f'{monitor2_name}_dnsperf数据'
#         elif roll == "monitor3":
#             title = f'{monitor3_name}_dnsperf数据'
#         dnsperfline = (
#             Line(init_opts=opts.InitOpts(width="1300px", height="500px"))
#                 .add_xaxis(xaxis_data=datatime_list)
#                 .add_yaxis(series_name='dnsperf data', y_axis=dnsperfdata_list, is_smooth=True)
#                 .set_global_opts(title_opts=opts.TitleOpts(title=title),
#                                  tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"))
#                 .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
#         )
#         dnsperfline.render(log_files_dict['dnsperf_html_with_path'])
#
#     def getRealtimeResolutionSuccessRate(self, roll="master"):
#         datatime = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(time.time()))
#         realtimeResolutionSuccessRate = self.DNS.getResolutionSuccessRate(roll)
#         if self.is_number(realtimeResolutionSuccessRate):
#             return [datatime, int(realtimeResolutionSuccessRate)]
#         else:
#             return [datatime, 0]
#
#     def getRealtimeResolutionSuccessRates(self):
#         resolutionSuccessRates_data_list = []
#         master_resolutionSuccessRates_datas = self.getRealtimeResolutionSuccessRate("master")
#         resolutionSuccessRates_data_list.append(master_resolutionSuccessRates_datas)
#         if monitor1.lower() == "true":
#             monitor1_resolutionSuccessRates_datas = self.getRealtimeResolutionSuccessRate("monitor1")
#             resolutionSuccessRates_data_list.append(monitor1_resolutionSuccessRates_datas)
#         else:
#             resolutionSuccessRates_data_list.append(0)
#         if monitor2.lower() == "true":
#             monitor2_resolutionSuccessRates_datas = self.getRealtimeResolutionSuccessRate("monitor2")
#             resolutionSuccessRates_data_list.append(monitor2_resolutionSuccessRates_datas)
#         else:
#             resolutionSuccessRates_data_list.append(0)
#         if monitor3.lower() == "true":
#             monitor3_resolutionSuccessRates_datas = self.getRealtimeResolutionSuccessRate("monitor3")
#             resolutionSuccessRates_data_list.append(monitor3_resolutionSuccessRates_datas)
#         else:
#             resolutionSuccessRates_data_list.append(0)
#         return resolutionSuccessRates_data_list
#
#     def writeRealtimeResolutionSuccessRateToCsv(self, resolutionSuccessRate_csv_with_path, datalist):
#         with open(resolutionSuccessRate_csv_with_path, "a+", encoding='utf-8', newline="") as e:
#             csv_writer = csv.writer(e)
#             csv_writer.writerow(datalist)
#
#     def drawResolutionSuccessRateLine(self, roll, log_files_dict):
#         datatime_list = []
#         resolutionSuccessRate_list = []
#         with open(log_files_dict['resolutionSuccessRate_csv_with_path'], 'r') as csvfile:
#             reader = csv.reader(csvfile)
#             for row in reader:
#                 datatime_list.append(row[0])
#                 resolutionSuccessRate_list.append(row[1])
#         if roll == "master":
#             title = 'master解析成功率数据'
#         elif roll == "monitor1":
#             title = f'{monitor1_name}解析成功率数据'
#         elif roll == "monitor2":
#             title = f'{monitor2_name}解析成功率数据'
#         elif roll == "monitor3":
#             title = f'{monitor3_name}解析成功率数据'
#         drawResolutionSuccessRateline = (
#             Line(init_opts=opts.InitOpts(width="1300px", height="500px"))
#                 .add_xaxis(xaxis_data=datatime_list)
#                 .add_yaxis(series_name='resolutionSuccessRate data', y_axis=resolutionSuccessRate_list, is_smooth=True)
#                 .set_global_opts(title_opts=opts.TitleOpts(title=title))
#                 .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
#         )
#         drawResolutionSuccessRateline.render(log_files_dict['resolutionSuccessRate_html_with_path'])
#
#     def getZdnsKeyProcessId(self, roll="master"):
#         try:
#             if roll == "master":
#                 zdns_id = self.RM_master.exec_cmd(
#                     'ps -ef | grep zdns.conf | grep -v grep | grep -v check | awk \'{print $2}\'')
#                 clouddns_id = self.RM_master.exec_cmd('ps -ef | grep cms_clouddns | grep -v grep | awk \'{print $2}\'')
#             elif roll == "monitor1":
#                 zdns_id = self.RM_monitor1.exec_cmd(
#                     'ps -ef | grep zdns.conf | grep -v grep | grep -v check | awk \'{print $2}\'')
#                 clouddns_id = self.RM_monitor1.exec_cmd(
#                     'ps -ef | grep cms_clouddns | grep -v grep | awk \'{print $2}\'')
#             elif roll == "monitor2":
#                 zdns_id = self.RM_monitor2.exec_cmd(
#                     'ps -ef | grep zdns.conf | grep -v grep | grep -v check | awk \'{print $2}\'')
#                 clouddns_id = self.RM_monitor2.exec_cmd(
#                     'ps -ef | grep cms_clouddns | grep -v grep | awk \'{print $2}\'')
#             elif roll == "monitor3":
#                 zdns_id = self.RM_monitor3.exec_cmd(
#                     'ps -ef | grep zdns.conf | grep -v grep | grep -v check | awk \'{print $2}\'')
#                 clouddns_id = self.RM_monitor3.exec_cmd(
#                     'ps -ef | grep cms_clouddns | grep -v grep | awk \'{print $2}\'')
#             if zdns_id is None or clouddns_id is None:
#                 return 0, 0
#             else:
#                 return zdns_id, clouddns_id
#         except Exception as e:
#             logger.error(f'get {roll} zdns_id or clouddns_id failed --- {e}')
#
#     def getMonitorZdnsKeyProcessId(self, roll):
#         try:
#             if roll == "monitor1":
#                 zdns_id = self.RM_monitor1.exec_cmd(
#                     'ps -ef | grep zdns.conf | grep -v grep | grep -v check | awk \'{print $2}\'')
#                 clouddns_id = self.RM_monitor1.exec_cmd(
#                     'ps -ef | grep cms_clouddns | grep -v grep | awk \'{print $2}\'')
#             if roll == "monitor2":
#                 zdns_id = self.RM_monitor2.exec_cmd(
#                     'ps -ef | grep zdns.conf | grep -v grep | grep -v check | awk \'{print $2}\'')
#                 clouddns_id = self.RM_monitor2.exec_cmd(
#                     'ps -ef | grep cms_clouddns | grep -v grep | awk \'{print $2}\'')
#             if roll == "monitor3":
#                 zdns_id = self.RM_monitor3.exec_cmd(
#                     'ps -ef | grep zdns.conf | grep -v grep | grep -v check | awk \'{print $2}\'')
#                 clouddns_id = self.RM_monitor3.exec_cmd(
#                     'ps -ef | grep cms_clouddns | grep -v grep | awk \'{print $2}\'')
#             if zdns_id is None or clouddns_id is None:
#                 return 0, 0
#             else:
#                 return zdns_id, clouddns_id
#         except Exception:
#             logger.error(f'get {roll} zdns_id or clouddns_id failed')
#
#     def checkId(self, ori, new):
#         if ori == new:
#             return 0
#         else:
#             return 1
#
#     def getCoredumpFileCount(self, roll="master"):
#         try:
#             if roll == "master":
#                 CoredumpCount = self.RM_master.exec_cmd(f'ls {dns_etc_dir} | grep core | wc -l')
#             elif roll == "monitor1":
#                 CoredumpCount = self.RM_monitor1.exec_cmd(f'ls {dns_etc_dir} | grep core | wc -l')
#             elif roll == "monitor2":
#                 CoredumpCount = self.RM_monitor2.exec_cmd(f'ls {dns_etc_dir} | grep core | wc -l')
#             elif roll == "monitor3":
#                 CoredumpCount = self.RM_monitor3.exec_cmd(f'ls {dns_etc_dir} | grep core | wc -l')
#             if CoredumpCount is None:
#                 return 0
#             else:
#                 return int(CoredumpCount)
#         except Exception as e:
#             logger.error(f'get {roll} CoredumpCount failed --- {e}')
#
#     def drawStatusPie(self, statusPie_html_with_path, zdns_id_tag, clouddns_id_tag, coredump_count, roll):
#         OK_Percentage = 100 - int(zdns_id_tag) - int(clouddns_id_tag) - int(coredump_count)
#         l1 = ['zdns_id_change', 'clouddns_id_change', 'coredump_count', 'OK_Percentage']
#         num = [int(zdns_id_tag), int(clouddns_id_tag), int(coredump_count), OK_Percentage]
#         if roll == "master":
#             title = f"master核心服务ID变化情况及coredump数量， OK_Percentage 100%为无问题"
#         elif roll == "monitor1":
#             title = f'{monitor1_name}核心服务ID变化情况及coredump数量， OK_Percentage 100%为无问题'
#         elif roll == "monitor2":
#             title = f'{monitor2_name}核心服务ID变化情况及coredump数量， OK_Percentage 100%为无问题'
#         elif roll == "monitor3":
#             title = f'{monitor3_name}核心服务ID变化情况及coredump数量， OK_Percentage 100%为无问题'
#         pie = (
#             Pie()
#                 .add(series_name="Percentage",
#                      data_pair=[(l1[0], num[0]), (l1[1], num[1]), (l1[2], num[2]), (l1[3], num[3])]).set_colors(
#                 ["#19ECED", "#9932CC", "#FF0000", "#00FF00"])
#                 #             .add("Percentage", [list(z) for z in zip(l1, num)])
#                 .set_global_opts(title_opts=opts.TitleOpts(title=title, pos_bottom="bottom", pos_right="center"))
#                 .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
#         )
#         pie.render(statusPie_html_with_path)
#
#     def time_trans(self, runtime):
#         if "d" in str(runtime).lower():
#             d_num = re.findall("\d+\.?\d*", runtime.replace(" ", ""))[0]
#             s_num = float(d_num) * 24 * 60 * 60
#         elif "h" in str(runtime).lower():
#             h_num = re.findall("\d+\.?\d*", runtime.replace(" ", ""))[0]
#             s_num = float(h_num) * 60 * 60
#         elif "m" in str(runtime).lower():
#             m_num = re.findall("\d+\.?\d*", runtime.replace(" ", ""))[0]
#             s_num = float(m_num) * 60
#         elif "s" in str(runtime).lower():
#             s_num = re.findall("\d+\.?\d*", runtime.replace(" ", ""))[0]
#         else:
#             s_num = 60
#             logger.info(f"input unsupported:{runtime}, stability will run in only {s_num}s")
#         return int(s_num)
#
#
