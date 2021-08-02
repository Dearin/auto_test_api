# -*- coding:utf-8 -*-
import sys

sys.path.append("../")
from conf.data_env_config import *
import random
import string
import re
import requests
import time


# from src.dns_maple.MapleDnsModule import *

def useDebug(func):
    def wrapper(*args, **kwargs):
        if debug_tag.lower() == "true":
            logger.debug(f'{func.__name__} is running')
            return func(*args)
        else:
            return func(*args)

    return wrapper


class BaseModule():
    def getCurrentStamp(self):
        '''get current mstime'''
        currTimes = time.time()
        mstime_stamp = int(round(currTimes * 1000))
        return mstime_stamp

    def get_random_ip(self):
        '''generate ipv4'''
        ip = str(random.randint(180, 223))
        for i in range(3):
            ip += "." + str(random.randint(1, 254))
        return ip

    def get_random_ipv6_ip(self):
        '''generate ipv6'''
        ip = "1133:2222:3333:2:5054:FF:FE5F:" + str(random.randint(1, 9999))
        return ip

    def get_long_zonename(self, len=8):
        '''generate zonename'''
        times = int((len - 4) / 64)
        zone = ''.join(
            random.choice(string.ascii_letters.lower() + string.ascii_letters.upper() + string.digits) for i in
            range(len - 4))
        zone = zone + ".cn."
        zone_list = list(zone)
        for i in range(times):
            i = i + 1
            zone_list[len - 4 - 64 * i] = "."
        zone = ''.join(zone_list)
        return zone.lower()

    # get random zone
    def get_random_zone(self):
        '''generate random zonename'''
        zone = ""
        label_count = random.randint(2, 6)
        for i in range(label_count):
            str = "abcdefghijklmnopqrstuvwxyz0123456789"
            single_label_length = random.randint(3, 10)
            label = ""
            for j in range(single_label_length):
                label = label + str[random.randint(0, len(str) - 1)]
            zone = zone + label + "."
        return zone

    def post_response(self, url, auth, data):
        '''post method'''
        resp = requests.post(url=url, auth=auth, data=data, headers=headers, verify=False)
        time.sleep(0.2)
        return resp.json(), resp.status_code

    def get_response(self, url, auth, data=None, params=None):
        '''get method'''
        if data == None:
            resp = requests.get(url=url, auth=auth, headers=headers, verify=False, params=params)
        else:
            resp = requests.get(url=url, auth=auth, data=data, headers=headers, verify=False, params=params)
        time.sleep(0.2)
        return resp.json(), resp.status_code

    def put_response(self, url, auth, data, int_data=None):
        '''put method'''
        resp = requests.put(url=url, auth=auth, data=data, headers=headers, verify=False)
        time.sleep(0.2)
        if int_data == "sp":
            return resp.status_code
        return resp.json(), resp.status_code

    def delete_response(self, url, auth, data):
        '''delete method'''
        resp = requests.delete(url=url, auth=auth, data=data, headers=headers, verify=False)
        time.sleep(0.2)
        return resp.json(), resp.status_code


if __name__ == "__main__":
    BM = BaseModule()
    #     zone_name = BM.get_long_zonename(5)
    #     send_result = BM.send_dnsperf()
    #     time = BM.time_trans(runtime)
    #     print(time)
    print(BM.getCurrentStamp())
