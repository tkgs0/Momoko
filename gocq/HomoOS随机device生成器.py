#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from uuid import uuid3, NAMESPACE_URL
from random import randint, choice
import hashlib, json


def is_number(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False


def get_random_imei() -> str:
    num = str(randint(10000000000000, 99999999999999))
    num_list = list(num)
    math_sum = 0
    for i in range(1, len(num_list)+1):
        if i % 2 == 0:
            take_two_num = int(num_list[i-1]) * 2
            if len(str(take_two_num)) == 2:
                for j in list(str(take_two_num)):
                    math_sum = int(j) + math_sum
            else:
                math_sum = take_two_num + math_sum
        else:
            math_sum = int(num_list[i-1]) + math_sum
    last_num = list(str(math_sum))[-1]
    if last_num == 0:
        check_num = 0
        imei = num + str(check_num)
        return imei
    else:
        check_num = 10 - int(last_num)
        imei = num + str(check_num)
        return imei


def mac(i: int = 0) -> str:
    i = i or randint(0,233)
    return hex(i).replace('0x','').rjust(2,'0')


def run(protocol: int) -> str:
    imei: str = get_random_imei()
    
    finger: str = ''.join([
        choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890")
        for _ in range(6)
    ])
    
    code: str = "114" + ''.join([str(randint(0,9)) for _ in range(4)]) + "514"
    
    url: str = f"android-build@{code}.source.android.com"
    
    default: dict = {
      "display": f"Android {randint(9,13)}",
      "product": "Product-ASS",
      "device": f"Homo X{(i := randint(1,6))}0",
      "board": "huawei",
      "model": f"ASS-{mac(i+32).upper()}{randint(1,4)}0",
      "finger_print": f"HOMO/PD1919/PD1919:10/{finger}/{code}:user/release-keys",
      "boot_id": str(uuid3(NAMESPACE_URL, url)),
      "proc_version": f"Linux version 5.1.4-generic ({url})",
      "protocol": protocol,
      "imei": imei,
      "brand": "HOMO",
      "bootloader": "unknown",
      "base_band": f"21C20B{randint(300,399)}S000C000",
      "version": {
        "incremental": code,
        "release": "10",
        "codename": "REL",
        "sdk": 29
      },
      "sim_info": choice(["giffgaff", "T-Mobile"]),
      "os_type": "android",
      "mac_address": (_mac_ := ':'.join([mac() for _ in range(6)]).upper()),
      "ip_address": [192, 168, randint(0,10), randint(2,200)],
      "wifi_bssid": _mac_,
      "wifi_ssid": "<unknown ssid>",
      "imsi_md5": hashlib.md5(imei.encode(encoding='UTF-8')).hexdigest(),
      "android_id": ''.join([mac() for _ in range(8)]),
      "apn": "wifi",
      "vendor_name": "HUAWEI",
      "vendor_os_name": "HomoOS"
    }
    
    with open('./device.json', 'w') as fd:
        fd.write(json.dumps(default, ensure_ascii=False, indent=2))

    return "`device.json`生成完毕."


if __name__ == "__main__":
    import sys
    arg: str = ''.join(sys.argv[1:2])
    if not is_number(arg) or int(arg) not in range(7):
        arg = input("请输入协议类型(0~6): ")
    if is_number(arg) and int(arg) in range(7):
        protocol: int = int(arg)
    else:
        protocol = 0
        print("未知参数, 使用默认值: 0")
    print(run(protocol))
