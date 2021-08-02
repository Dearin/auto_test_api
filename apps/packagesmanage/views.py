from django.views.generic import View
from loguru import logger
from libs.tool import json_response, conver_byte_to_utf8
import datetime
import time
import json
import threading

from conf.ENV_CONF import RPM_SERVER_CENTOS78, RPM_SERVER_CENTOS64, VSPHERE_SERVER, RPM_SAVE_SERVER
from libs.operateVsPhere import OperateVSphere
from libs.RemoteOperate import RemoteModule


ssh_78 = RemoteModule(
    ip=RPM_SERVER_CENTOS78['host'],
    user=RPM_SERVER_CENTOS78['username'],
    passwd=RPM_SERVER_CENTOS78['password']
)

ssh_64 = RemoteModule(
    ip=RPM_SERVER_CENTOS64['host'],
    user=RPM_SERVER_CENTOS64['username'],
    passwd=RPM_SERVER_CENTOS64['password']
)

rpm_save_server_ssh = RemoteModule(
            ip=RPM_SAVE_SERVER['host'],
            user=RPM_SAVE_SERVER['username'],
            passwd=RPM_SAVE_SERVER['password']
        )

vm_name_centos6 = VSPHERE_SERVER['vm_name_centos6']
vm_name_centos7 = VSPHERE_SERVER['vm_name_centos7']
snapshot_name = VSPHERE_SERVER['snapshot_name']
centos6_rpm_path = RPM_SERVER_CENTOS64['path']
centos7_rpm_path = RPM_SERVER_CENTOS78['path']


def start_exec_rpm(ssh, command):
    logger.info("开始制作rpm命令:{0}".format(command))
    ssh.exec_command(command)


class HandleRpmMake(View):

    def post(self, request):
        """
        RPM包制作步骤：
            1.校验RRM包服务上是否有对应的RPM制作进程存在
            2.初始化vsphere平台上虚拟机的环境（恢复快照到最初始环境）
            3.在初始的化的环境中，先git pull代码，git chcekout -f branch切到对应的分支
            4.制作rpm包，替换制作rpm包脚本中的日期为当前时间
            5.如果配置了邮件，则需要加上对应的发送邮件配置
            6.执行制作rpm脚本， cd /root/zddi-build-7.8, 执行./install.sh --force  && gen_rpm.sh
            7.rpm制作完成后，将生的的rpm通过scp拷贝到自动化平台服务器
        """
        data = request.body
        data = data.decode('utf-8')
        data = json.loads(data) if data else {}
        email = data.get("email") if data.get("email") else ""
        email = email.replace("，", ",")

        rpm_exist_comm = rpm_save_server_ssh.exec_command("ls /opt/rpm")

        if not rpm_exist_comm:
            logger.info("服务器{0}上不存在目录:{1}, 新建该目录".format(
                RPM_SAVE_SERVER['host'],
                RPM_SAVE_SERVER['path']
            ))
            rpm_save_server_ssh.exec_command("mkdir -p {0}".format(RPM_SAVE_SERVER['path']))

        operate_vsphere = OperateVSphere(
            host=VSPHERE_SERVER['host'],
            user=VSPHERE_SERVER['user'],
            password=VSPHERE_SERVER['password'],
            port=VSPHERE_SERVER['port']
        )

        if not operate_vsphere.init_connect():
            logger.info("vsphere连接异常，请检查")
            return json_response(error="vsphere连接异常，请检查")

        if data.get("type") == "centos78":
            check_rpm_exist = "ps aux|grep -E 'rpm|fpm|install.sh --force'|grep -v 'scp'|grep -v grep|wc -l"
            rpm_exist = ssh_78.exec_command(check_rpm_exist)
            if rpm_exist != '0':
                return json_response(error="有rpm包正在制作，请稍后重试")

            check_install_script_exist = ssh_78.exec_command("ls {0} | grep install.sh".format(centos7_rpm_path))
            logger.info("制作rpm包，检查{0}分支下面是否存在install.sh:{1}".format(
                data['branch'],
                check_install_script_exist
            ))

            if not check_install_script_exist:
                return json_response(error="{0}分支下面不存在install.sh， 与制作脚本不符，请检查！")
            git_pull_out = ssh_78.exec_command("cd {0} && git pull".format(centos7_rpm_path))
            logger.info("制作rpm包，git pull输出：{0}".format(git_pull_out))

            checkout_git = ssh_78.exec_command_err(
                "cd {0} && git checkout -f {1}".format(centos7_rpm_path, data['branch']))
            logger.info("制作rpm包，git checkout输出:{0}".format(checkout_git))
            if 'error' in checkout_git:
                return json_response(error="{0}分支可能有误，请检查！".format(data['branch']))

            is_re_snapshot_ok = operate_vsphere.re_snapshot(vm_name_centos7, snapshot_name)
            logger.info("在vsphere恢复虚拟机快照状态：{0}".format(is_re_snapshot_ok))
            if not is_re_snapshot_ok:
                return json_response(error="在vsphere恢复虚拟机快照失败")
            time.sleep(15)  # 等待虚拟机重启
            # 获取虚拟机电源状态
            vm_power_status = operate_vsphere.get_vm_info(vm_name_centos7).powerState
            logger.info("获取虚拟机的电源状态：{0}".format(vm_power_status))
            if vm_power_status != 'poweredOn':
                return json_response(error="虚拟机启动失败！")

            current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            log_name = "{0}zddi-build-{1}.el7.log".format(centos7_rpm_path, current_time)
            # logger.info("log_name:{0}".format(log_name))

            rpm_save_server_ssh.exec_command(
                'echo "RPM包正在制作，请等待....." >> {0}/zddi-build-{1}.el7.log'.format(RPM_SAVE_SERVER['path'], current_time)
            )

            # 更新服务器时间
            ssh_78.exec_command("/usr/sbin/ntpdate ntp1.aliyun.com")

            ssh_78.exec_command("cd {0} && git pull > {1}".format(centos7_rpm_path, log_name))
            ssh_78.exec_command_err(
                "cd {0} && git checkout -f {1} >> {2}".format(centos7_rpm_path, data['branch'], log_name))

            # 查看当前的分支信息
            ssh_78.exec_command("cd {0} && git branch >> {1}".format(centos7_rpm_path, log_name))
            # 执行make pull更新dns
            ssh_78.exec_command("cd {0} && make pull >> {1}".format(centos7_rpm_path, log_name))

            # 替换制作rpm脚本
            relpace_ver_date = ssh_78.exec_command(
                'grep -n "ver_date=\$(date +%Y%m%d)" {0}gen_rpm.sh'.format(centos7_rpm_path))
            if relpace_ver_date:
                ssh_78.exec_command(
                    """sed -i 's/\$(date +%Y%m%d)/"{0}"/g' {1}gen_rpm.sh""".format(
                        current_time, centos7_rpm_path))
                logger.info("替换gen_rpm.sh脚本中生成rpm的时间戳")
            else:
                return json_response(error="制作rpm的脚本{0}gen_rpm.sh可能不存在，请检查")

            # 删除rpm包的安装脚本
            ssh_78.exec_command(
                """ sed -i "/install_rpm\.sh/d" {0}gen_rpm.sh""".format(centos7_rpm_path)
            )

            # 在gen_rpm.sh的脚本的首行添加install.sh --force的行
            ssh_78.exec_command(
                """ sed -i "1i./install.sh --force" {0}gen_rpm.sh""".format(centos7_rpm_path)
            )
            logger.info("制作rpm包，在gen_rpm.sh的脚本的首行添加install.sh --force的行")

            # 增加scp命令，传输rpm到远端服务器
            ssh_78.exec_command(
                'echo "scp {0}zddi-build-{1}.log root@{2}:{3}">> {0}gen_rpm.sh'.format(
                    centos7_rpm_path,
                    current_time,
                    RPM_SAVE_SERVER['host'],
                    RPM_SAVE_SERVER['path']
                )
            )
            ssh_78.exec_command(
                'echo "scp {0}zddi*.rpm root@{1}:{2}">> {0}gen_rpm.sh'.format(
                    centos7_rpm_path,
                    RPM_SAVE_SERVER['host'],
                    RPM_SAVE_SERVER['path']
                )
            )
            if email:
                insert_send_email = """
send_name=\`ls {0}| grep \$ver_date | grep -v log| grep -v grep\`
/usr/bin/python /root/sendEmail1.py {1} {2} \$send_name
                               """.format(centos7_rpm_path, email, RPM_SAVE_SERVER['host'])
                ssh_78.exec_command(
                    'echo "{0}">> {1}gen_rpm.sh'.format(insert_send_email, centos7_rpm_path)
                )

            ssh_78.exec_command("cd {0} && git diff >> {1}".format(
                centos7_rpm_path,
                log_name
            ))

            command = "cd {0} && ./gen_rpm.sh >> {1} 2>&1 &".format(centos7_rpm_path, log_name)

            exec_make_rpm_comm = threading.Thread(target=start_exec_rpm, args=(ssh_78, command))
            exec_make_rpm_comm.start()

            logger.info("RPM服务器{0}开始制作RPM......".format(RPM_SERVER_CENTOS78['host']))

        elif data.get("type") == "centos64":
            check_rpm_exist_comm = "ps aux|grep -E 'rpm|fpm|auto_gem_rpm.sh'|grep -v grep|wc -l"
            check_rpm_exist_out = ssh_64.exec_command(check_rpm_exist_comm)
            if check_rpm_exist_out != '0':
                return json_response(error="有rpm包正在制作，请稍后重试")

            ssh_64.exec_command("cd {0} && git pull".format(centos6_rpm_path))
            checkout_git = ssh_64.exec_command_err(
                "cd {0} && git checkout -f {1}".format(centos6_rpm_path, data['branch']))
            logger.info("检查分支是否存在：{0}".format(data['branch']))
            if 'error' in checkout_git:
                return json_response(error="{0}分支可能有误，请检查！".format(data['branch']))

            is_re_snapshot_ok = operate_vsphere.re_snapshot(vm_name_centos6, snapshot_name)
            logger.info("在vsphere恢复虚拟机快照状态：{0}".format(is_re_snapshot_ok))
            if not is_re_snapshot_ok:
                return json_response(error="在vsphere恢复虚拟机快照失败")
            time.sleep(15)  # 等待虚拟机重启
            # 获取虚拟机电源状态
            vm_power_status = operate_vsphere.get_vm_info(vm_name_centos6).powerState
            logger.info("获取虚拟机的电源状态：{0}".format(vm_power_status))
            if vm_power_status != 'poweredOn':
                return json_response(error="虚拟机启动失败！")

            current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            log_name = "{0}zddi-build-{1}.el6.log".format(centos6_rpm_path, current_time)

            rpm_save_server_ssh.exec_command(
                'echo "RPM包正在制作，请等待....." >> {0}/zddi-build-{1}.el6.log'.format(
                    RPM_SAVE_SERVER['path'],
                    current_time)
            )

            # 更新服务器时间
            ssh_64.exec_command("/usr/sbin/ntpdate ntp1.aliyun.com")

            ssh_64.exec_command("cd {0} && git pull > {1}".format(centos6_rpm_path, log_name))
            ssh_64.exec_command_err(
                "cd {0} && git checkout -f {1} >> {2}".format(centos6_rpm_path, data['branch'], log_name))

            # 查看当前的分支信息
            ssh_64.exec_command("cd {0} && git branch >> {1}".format(centos6_rpm_path, log_name))
            ssh_64.exec_command("cd {0}/ && make pull >> {1}".format(centos6_rpm_path, log_name))

            # 替换制作rpm脚本
            relpace_ver_date = ssh_64.exec_command(
                'grep -n "ver_date=\$(date +%Y%m%d)" {0}/repo/gen_rpm.sh'.format(centos6_rpm_path))
            if relpace_ver_date:
                ssh_64.exec_command(
                    """sed -i 's/\$(date +%Y%m%d)/"{0}"/g' {1}/repo/gen_rpm.sh""".format(current_time, centos6_rpm_path))
            else:
                return json_response(error="制作rpm的脚本{0}/repo/gen_rpm.sh不存在，请检查".format(centos6_rpm_path))

            # 删除rpm包的安装rpm脚本
            ssh_64.exec_command(
                """ sed -i "/install_rpm\.sh/d" {0}/auto_gem_rpm.sh""".format(centos6_rpm_path)
            )

            # 增加scp命令，传输rpm到远端服务器
            ssh_64.exec_command(
                'echo "scp {0}zddi-build-{1}.log root@{2}:{3}">> {0}/repo/gen_rpm.sh'.format(
                    centos6_rpm_path,
                    current_time,
                    RPM_SAVE_SERVER['host'],
                    RPM_SAVE_SERVER['path']
                )
            )
            ssh_64.exec_command(
                'echo "scp {0}zddi*.rpm root@{1}:{2}">> {0}/repo/gen_rpm.sh'.format(
                    centos6_rpm_path,
                    RPM_SAVE_SERVER['host'],
                    RPM_SAVE_SERVER['path']
                )
            )
            if email:
                insert_send_email = """
send_name=\`ls {0}| grep \$ver_date | grep -v log| grep -v grep\`
/usr/bin/python /root/sendEmail1.py {1} {2} \$send_name
                   """.format(centos6_rpm_path, email, RPM_SAVE_SERVER['host'])
                ssh_64.exec_command(
                    'echo "{0}">> {1}/repo/gen_rpm.sh'.format(insert_send_email, centos6_rpm_path)
                )

            ssh_64.exec_command("cd {0} && git diff >> {1}".format(centos6_rpm_path, log_name))
            command = "cd {0} && ./auto_gem_rpm.sh >> {1} 2>&1 &".format(centos6_rpm_path, log_name)
            exec_make_rpm_comm = threading.Thread(target=start_exec_rpm, args=(ssh_64, command))
            exec_make_rpm_comm.start()

            logger.info("RPM服务器{0}开始制作RPM......".format(RPM_SERVER_CENTOS64['host']))

        respone = {
            "code": 200
        }
        return json_response(respone)

    def get(self, request):
        get_file_list = 'ls {0} | grep "zddi"'.format(RPM_SAVE_SERVER['path'])
        data = []
        if get_file_list:
            file_lists = rpm_save_server_ssh.exec_command(get_file_list).split("\n")
            file_log = {
                "el6": [],
                "el7": []
            }
            file_rpm = {
                "el6": [],
                "el7": []
            }
            all_rpm_time = {
                "el7": [],
                "el6": []
            }

            for file in file_lists:
                if "log" in file:
                    if 'el7' in file:
                        file_log['el7'].append(file)
                    else:
                        file_log['el6'].append(file)
                elif "rpm" in file:
                    if 'el7' in file:
                        all_rpm_time['el7'].append(file[-29:-15])
                        file_rpm['el7'].append(file)
                    else:
                        file_rpm['el6'].append(file)
                        all_rpm_time['el6'].append(file[-25:-11])

            # 处理centos64
            for i in file_log['el6']:
                res = dict()
                time_flag = i[-22:-8]
                res['key'] = time_flag
                res['ip_addr'] = RPM_SERVER_CENTOS64['host']
                res['rpm_log'] = i
                if time_flag not in all_rpm_time['el6']:
                    download_log_comm = "scp root@{0}:{1}zddi-*{2}.el6.log {3}".format(
                        RPM_SERVER_CENTOS64['host'],
                        RPM_SERVER_CENTOS64['path'],
                        time_flag,
                        RPM_SAVE_SERVER['path']
                    )
                    # logger.info(download_log_comm)
                    download_log_info = rpm_save_server_ssh.exec_command_err(download_log_comm)
                    if "No such file or directory" in download_log_info:
                        res['rpm_name'] = 'rpm包制作失败...'
                    elif "timed out" in download_log_info or "No route to host" in download_log_info:
                        res['rpm_name'] = '连接rpm制作服务器{0}超时...'.format(RPM_SERVER_CENTOS64['host'])
                    else:
                        check_rpm_exist_comm = "ps aux|grep -E 'rpm|fpm|auto_gem_rpm.sh'|grep -v grep|wc -l"
                        check_rpm_exist_out = ssh_64.exec_command(check_rpm_exist_comm)
                        if check_rpm_exist_out == '0':
                            res['rpm_name'] = 'rpm包出错，请查看日志...'
                        else:
                            res['rpm_name'] = 'rpm制作中...'
                else:
                    for j in file_rpm['el6']:
                        if time_flag in j:
                            res['rpm_name'] = j
                            res['rpm_download'] = "scp root@{0}:{1}{2} ./".format(
                                RPM_SAVE_SERVER['host'],
                                RPM_SAVE_SERVER['path'],
                                j
                            )
                data.append(res)
            # 处理centos78
            for i in file_log['el7']:
                res = dict()
                time_flag = i[-22:-8]
                res['key'] = time_flag
                res['ip_addr'] = RPM_SERVER_CENTOS78['host']
                res['rpm_log'] = i
                if time_flag not in all_rpm_time['el7']:
                    download_log_comm = "scp root@{0}:{1}zddi-*{2}.el7.log {3}".format(
                        RPM_SERVER_CENTOS78['host'],
                        RPM_SERVER_CENTOS78['path'],
                        time_flag,
                        RPM_SAVE_SERVER['path']
                    )
                    logger.info(download_log_comm)
                    download_log_info = rpm_save_server_ssh.exec_command_err(download_log_comm)
                    # logger.info("el7:{0}".format(download_log_info))
                    if "No such file or directory" in download_log_info:
                        res['rpm_name'] = 'rpm包制作失败...'
                    elif "timed out" in download_log_info or "No route to host" in download_log_info:
                        res['rpm_name'] = '连接rpm制作服务器{0}超时...'.format(RPM_SERVER_CENTOS78['host'])
                    else:
                        check_rpm_exist = "ps aux|grep -E 'rpm|fpm|install.sh --force'|grep -v 'scp'|grep -v grep|wc -l"
                        rpm_exist = ssh_78.exec_command(check_rpm_exist)
                        if rpm_exist == '0':
                            res['rpm_name'] = 'rpm包出错，请查看日志...'
                        else:
                            res['rpm_name'] = 'rpm制作中...'
                else:
                    for j in file_rpm['el7']:
                        if time_flag in j:
                            res['rpm_name'] = j
                            res['rpm_download'] = "scp root@{0}:{1}{2} ./".format(
                                RPM_SAVE_SERVER['host'],
                                RPM_SAVE_SERVER['path'],
                                j
                            )
                data.append(res)

        data = sorted(data, key=lambda e: e.__getitem__('key').split("-")[-1], reverse=True)
        respone = {
            "code": 200,
            "data": data
        }
        return json_response(respone)


class HandleRpmLog(View):
    def get(self, request):
        log_name = request.GET.get('log_name')
        log_detail_comm = 'cat {0}{1}'.format(RPM_SAVE_SERVER['path'], log_name)
        log_detail = rpm_save_server_ssh.exec_command(log_detail_comm).split("\n")
        respone = {
            "code": 200,
            "data": log_detail
        }

        return json_response(respone)


class HandleTarMake(View):

    def __init__(self):
        self.tar_path = RPM_SAVE_SERVER['tar_path']

    def post(self, request):
        data = request.body
        data = data.decode('utf-8')
        data = json.loads(data) if data else {}

        check_rpm_exist = "ps aux|grep publisher |grep -v grep|wc -l"
        rpm_exist = rpm_save_server_ssh.exec_command(check_rpm_exist)
        if rpm_exist != '0':
            return json_response(error="有tar包正在制作，请稍后重试")

        git_res = rpm_save_server_ssh.exec_command_err(
            "cd {0}zddi && git checkout -f {1}".format(self.tar_path, data['branch']))

        if 'error' in git_res:
            return json_response(error="{0}分支可能有误，请检查！".format(data['branch']))

        rpm_save_server_ssh.exec_command(
            "cd {0}zddi && git pull".format(self.tar_path))

        # 执行git submodule update，关联前台分支
        rpm_save_server_ssh.exec_command(
            "cd {0} && git submodule update".format(self.tar_path))

        if data.get("tarName"):
            tar_name = data['tarName']
        else:
            # 在搭建环境的时候，需要将get_version.sh的脚本复制到对应的目录
            tar_name = rpm_save_server_ssh.exec_command('/opt/tar/get_version.sh')

        current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        log_name = "{0}zddi-{1}-{2}.log".format(self.tar_path, tar_name, current_time)

        rpm_save_server_ssh.exec_command("cd {0}zddi && git pull > {1}".format(self.tar_path, log_name))

        command = "/usr/bin/publisher -c release -v {0}-{1} -d {2}/zddi >> {3} 2>&1 &".format(
            tar_name,
            current_time,
            self.tar_path,
            log_name,
        )
        logger.info("制作tar包，命令：{0}".format(command))

        rpm_save_server_ssh.exec_command(command)

        respone = {
            "code": 200
        }
        return json_response(respone)

    def get(self, request):
        get_file_list = 'ls {0} | grep "zddi-"'.format(self.tar_path)
        data = []
        file_lists = rpm_save_server_ssh.exec_command(get_file_list).split("\n")

        file_log = []
        file_tar = []

        for file in file_lists:
            if "log" in file:
                file_log.append(file)
            elif "tar.gz" in file:
                file_tar.append(file)

        for i in file_log:
            res = dict()
            time_flag = i[-18:-4]
            res['key'] = time_flag
            res['ip_addr'] = RPM_SAVE_SERVER['host']
            res['tar_log'] = i
            tar_name = "{0}.tar.gz".format(i[:-4])
            res['tar_name'] = tar_name if tar_name in file_tar else 'tar制作中...'
            res['tar_download'] = "scp root@{0}:{1}{2} ./".format(
                RPM_SAVE_SERVER['host'],
                RPM_SAVE_SERVER['tar_path'],
                res['tar_name']
            )
            data.append(res)
        data = sorted(data, key=lambda e: e.__getitem__('key').split("-")[-1], reverse=True)
        respone = {
            "code": 200,
            "data": data
        }
        return json_response(respone)


class HandleTarLog(View):
    def get(self, request):
        log_name = request.GET.get('log_name')
        log_detail_comm = 'cat {0}{1}'.format(RPM_SAVE_SERVER['tar_path'], log_name)
        log_detail = rpm_save_server_ssh.exec_command(log_detail_comm).split("\n")

        respone = {
            "code": 200,
            "data": log_detail
        }
        return json_response(respone)


