# -*- coding: utf-8 -*-
# @Time    : 2021/5/19 13:42
# @Author  : weidengyi


RPM_SERVER_CENTOS78 = {
    'host': '10.1.107.32',
    'username': 'root',
    'password': 'zdns@knet.cn',
    'path': '/root/zddi-build-7.8/'
}

RPM_SERVER_CENTOS64 = {
    'host': '10.1.107.31',
    'username': 'root',
    'password': 'zdns@knet.cn',
    'path': '/root/zddi-build-v4/'
}

RPM_SAVE_SERVER = {
    'host': '10.1.107.30',
    'username': 'root',
    'password': 'zdns@knet.cn',
    'path': '/opt/rpm/',
    'tar_path': '/opt/tar/'
}

CODE_COVERAGE_SERVER = {
    'host': '10.2.2.41',
    'username': 'root',
    'password': 'zdns@knet.cn',
    'zddiv3_path': '/root/zddiv3'
}

VSPHERE_SERVER = {
    'host': '10.1.107.200',
    'user': 'zhanglichao',
    'password': 'zhanglichao@zdns',
    'port': 443,
    'snapshot_name': "初始环境",
    'vm_name_centos6': "10.1.107.31-centos64",
    'vm_name_centos7': "10.1.107.32-centos78"
}