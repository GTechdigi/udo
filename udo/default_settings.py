# coding: utf-8

import os
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from udo.apollo.apollo_client import ApolloClient


apollo_config_url = os.environ.get("APOLLO_URL")  # or 'https://apollo-meta-xxxx.xxxx.xxxxx'
client = ApolloClient(app_id="svc-codex-udo", cluster="default", config_url=apollo_config_url)
env_str = client.get_value("ENV", default_val="DEV")
UDO_BIND = client.get_value("UDO_BIND", default_val="0.0.0.0")
UDO_PORT = client.get_int_value("UDO_PORT", default_val=5000)
DEBUG = client.get_bool_value("DEBUG", default_val="True")
USE_RELOADER = client.get_bool_value("USE_RELOADER", default_val=False)
# The default is False, set it to True to enable basic auth for the web UI.
ENABLE_AUTH = client.get_bool_value("ENABLE_AUTH", default_val=False)
# In order to enable basic auth, both USERNAME and PASSWORD should be non-empty strings.
USERNAME = client.get_value("USERNAME", default_val='')
PASSWORD = client.get_value("PASSWORD", default_val='')


ENABLE_HTTPS = client.get_bool_value("ENABLE_HTTPS", default_val=False)
# e.g. '/home/username/cert.pem'
CERTIFICATE_FILEPATH = client.get_value("CERTIFICATE_FILEPATH", default_val='')
# e.g. '/home/username/cert.key'
PRIVATEKEY_FILEPATH = client.get_value("PRIVATEKEY_FILEPATH", default_val='')

JSON_AS_ASCII = client.get_bool_value("JSON_AS_ASCII", default_val=False)

REDIS_URL = client.get_value("REDIS_URL", default_val="redis://xxxxxx:6379/15")

SQLALCHEMY_DATABASE_URI = client.get_value("SQLALCHEMY_DATABASE_URI", default_val='mysql+pymysql://username:password@127.0.0.1:3306/dev_udo_db?charset=utf8')
SQLALCHEMY_COMMIT_ON_TEARDOWN = client.get_bool_value("SQLALCHEMY_COMMIT_ON_TEARDOWN", default_val=True)
SQLALCHEMY_TRACK_MODIFICATIONS = client.get_bool_value("SQLALCHEMY_TRACK_MODIFICATIONS", default_val=True)
SQLALCHEMY_ECHO = client.get_bool_value("SQLALCHEMY_ECHO", default_val=True)

SQLALCHEMY_POOL_SIZE = client.get_int_value("SQLALCHEMY_POOL_SIZE", default_val=20)
SQLALCHEMY_POOL_TIMEOUT = 300
SQLALCHEMY_MAX_OVERFLOW = client.get_int_value("SQLALCHEMY_MAX_OVERFLOW", default_val=5)
# 域帐号相关配置
LDAP_HOST = client.get_value("LDAP_HOST", default_val='xxxxxxxx')
LDAP_PORT = client.get_int_value("LDAP_PORT", default_val=389)
LDAP_BASE = client.get_value("LDAP_BASE", default_val='OU=xxxx,DC=xxxx,DC=com')
LDAP_USER = client.get_value("LDAP_USER", default_val='xxxxx@xxxx.com')
LDAP_PASSWORD = client.get_value("LDAP_PASSWORD", default_val='xxxxx')


SCHEDULER_JOBSTORES = {
    'default': SQLAlchemyJobStore(url=client.get_value("SCHEDULER_JOBSTORES_URL", default_val='mysql+pymysql://username:password@127.0.0.1:3306/dev_udo_db?charset=utf8'),
                                  tablename=client.get_value("SCHEDULER_JOBSTORES_TABLENAME", default_val='udo_job'))
}

SCHEDULER_EXECUTORS = {
    'default': ThreadPoolExecutor(client.get_int_value("SCHEDULER_EXECUTORS_THREAD_MAX_WORKERS", default_val=20)),
    'processpool': ProcessPoolExecutor(client.get_int_value("SCHEDULER_EXECUTORS_PROCESS_MAX_WORKERS", default_val=5))
}

SCHEDULER_JOBDEFAULTS = {
    'coalesce': client.get_bool_value("SCHEDULER_JOBDEFAULTS_COALESCE", default_val=False),
    'max_instances': client.get_int_value("SCHEDULER_JOBDEFAULTS_MAX_INSTANCES", default_val=3)
}

# 用于公司内部邮件服务
GATEWAY_URL = client.get_value("GATEWAY_URL", default_val='http://gateway.xxx/api')
GATEWAY_APP_ID = client.get_value("GATEWAY_APP_ID", default_val='xxxxx')
GATEWAY_APP_SECRET = client.get_value("GATEWAY_APP_SECRET", default_val='xxxxxxxx')

ADMIN = client.get_value("ADMIN", default_val='admin')

# oss相关配置
OSS_ACCESS_KEY_ID = client.get_value("OSS_ACCESS_KEY_ID", default_val='xxxx')
OSS_ACCESS_KEY_SECRET = client.get_value("OSS_ACCESS_KEY_SECRET", default_val='xxxxx')
OSS_BUCKET = client.get_value("OSS_BUCKET", default_val='xxxxxxx')
OSS_ENDPOINT = client.get_value("OSS_ENDPOINT", default_val='oss-cn-xxxxxx.aliyuncs.com')
EXCEL_DIR = client.get_value("EXCEL_DIR", default_val='/tmp/')
# false 不开启kerberos认证
HAVE_KERBEROS = client.get_bool_value("HAVE_KERBEROS", default_val=False)
KERBEROS_DOMAIN = client.get_value("KERBEROS_DOMAIN", default_val="xxxxxxx")

EMAIL_CONTENT_ROW = client.get_int_value("EMAIL_CONTENT_ROW", default_val=10)


