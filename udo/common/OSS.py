# -*- coding: utf-8 -*-

from udo import default_settings
import oss2
import time
import os
import random


# 以下代码展示了文件上传的高级用法，如断点续传、分片上传等。
# 基本的文件上传如上传普通文件、追加文件，请参见object_basic.py


# 首先初始化AccessKeyId、AccessKeySecret、Endpoint等信息。
# 通过环境变量获取，或者把诸如“<你的AccessKeyId>”替换成真实的AccessKeyId等。
#
# 以杭州区域为例，Endpoint可以是：
#   http://oss-cn-hangzhou.aliyuncs.com
#   https://oss-cn-hangzhou.aliyuncs.com
# 分别以HTTP、HTTPS协议访问。

def upload(file_name: str, origin_file: str):
    access_key_id = default_settings.OSS_ACCESS_KEY_ID
    access_key_secret = default_settings.OSS_ACCESS_KEY_SECRET
    bucket_name = default_settings.OSS_BUCKET
    endpoint = default_settings.OSS_ENDPOINT

    # 创建Bucket对象，所有Object相关的接口都可以通过Bucket对象来进行
    bucket = oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, bucket_name)
    if file_name.endswith(".xlsx"):
        file_name = file_name[0: -5] + str(random.randint(1000, 9999)) + '.xlsx'

    oss_file_path = 'udo/' + time.strftime('%Y%m%d', time.localtime()) + '/' + file_name
    bucket.put_object_from_file(oss_file_path, origin_file)
    os.remove(origin_file)
    return 'https://' + bucket_name + '.' + endpoint + '/' + oss_file_path
    # 上传一段字符串。Object名是motto.txt，内容是一段名言。
    # bucket.put_object(oss_file_path, 'Never give up. - Jack Ma')
    # print('https://' + bucket_name + '.' + endpoint + '/' + oss_file_path)

