import os
import json
import time, datetime
from django.http.response import HttpResponse
from libs.tool import timestamp_to_str, json_response
import logging
from libs.ssh import SSH
from conf.ENV_CONF import CODE_COVERAGE_SERVER

# Create your views here.
logging.basicConfig(level=logging.DEBUG,filename='/root/dhcp.log',
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')


# Create your views here.
ssh = SSH(hostname=CODE_COVERAGE_SERVER['host'], username=CODE_COVERAGE_SERVER['username'], password=CODE_COVERAGE_SERVER['password'])
client = ssh.get_client()


#获取文件后缀
def getsuffix(filename):
    suffix = filename.split(".")
    return suffix[len(suffix)-1]


def get_code_coverage_report(request):
    path = "/root/coverage/sample/report/"

    stdin, stdout, stderr = client.exec_command('ls /root/coverage/sample/report|grep -E "log|html"')
    file_lists = stdout.read().decode('utf-8')[:-1].split("\n")

    file_log = []
    file_html = []
    data = []
    for file in file_lists:
        if "log" in file:
            file_log.append(file)
        elif "html" in file:
            file_html.append(file)

    for i in file_log:
        res = dict()
        time_flag = i.split(".")[0]
        res['key'] = time_flag
        res['time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time_flag)))
        res['branch'] = ''
        res['report'] = '运行中....'
        res["log"] = i
        for j in file_html:
            if time_flag in j:
                file_html.remove(j)
                res['branch'] = j.split("_")[0]
                res['report'] = j
                res['url'] = path + j
        data.append(res)

    data = sorted(data, key=lambda e: e.__getitem__('time'), reverse=True)
    return json_response(data)


def handle_rake_log(request):
    log_name = request.GET.get('log')
    stdin, stdout, stderr = client.exec_command('cat /root/coverage/sample/report/{0}'.format(log_name))
    log_detail = stdout.read().decode('utf-8')[:-1].split("\n")
    respone = {
        "code": 200,
        "data": log_detail
    }
    return json_response(respone)


def handle_rake_test(request):
    data = request.body
    data = data.decode('utf-8')
    data = json.loads(data) if data else {}

    client.exec_command("cd {0} && git pull".format(CODE_COVERAGE_SERVER['zddiv3_path']))
    branch = data['branch'].strip()
    stdin, stdout, stderr = client.exec_command(
        "cd {0} && git checkout -f {1}".format(CODE_COVERAGE_SERVER['zddiv3_path'], branch))
    git_res = stderr.read().decode('utf-8')
    if 'error' in git_res:
        return json_response(error="{0}分支可能有误，请检查！".format(branch))

    check_rake_exist = "ps aux|grep -E 'rake'|grep -v grep|wc -l"
    stdin, stdout, stderr = client.exec_command(check_rake_exist)
    rpm_exist = stdout.read().decode('utf-8')[:-1]
    if rpm_exist != '0':
        return json_response(error="有代码覆盖率正在进行，请稍后重试")

    # 配置分支名称
    # current_time = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    current_time = int(time.time())
    client.exec_command('sed -i "/name:/d" /opt/auto_test_api/conf/conf.yml')
    client.exec_command('sed -i "/create_html:/d" /opt/auto_test_api/conf/conf.yml')
    time.sleep(0.5)
    client.exec_command('/bin/echo "name: {0}" >> /opt/auto_test_api/conf/conf.yml'.format(branch))
    client.exec_command('/bin/echo "create_html: {0}" >> /opt/auto_test_api/conf/conf.yml'.format(current_time))

    client.exec_command(
        'cd /root/coverage/sample/ && /usr/local/bin/rake test >> /root/coverage/sample/report/{0}.log'.format(
            current_time))

    data = {
        'code': 200,
        'msg': 'success'
    }
    return json_response(data)


def test(request):
    if request.body:
        print(json.loads(request.body))
        logging.info(json.loads(request.body))
    return HttpResponse(json.dumps({"code": 200}), content_type='application/json')
