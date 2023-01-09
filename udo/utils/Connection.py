import clickhouse_driver
from impala.dbapi import connect
import pymysql
import requests
from udo import default_settings
import os
from krbcontext import krbcontext
from log import logger


def __mysql(config, sql="select 1", where_values=None, limit=1000):
    if not where_values:
        where_values = None
    db = pymysql.connect(host=config["host"], user=config["user"], port=int(config["port"]),
                         password=config["password"], database=config["db_name"])
    cursor = db.cursor()
    try:
        if sql == 'show tables':
            cursor.execute(sql)
        else:
            cursor.execute(sql + ' limit ' + str(limit), where_values)
        result = cursor.fetchall()
        return result
    except Exception as e:
        logger.error(e)
        raise e
    finally:
        cursor.close()
        db.close()


def __hive(config, sql="select 1", where_values=None, limit=1000):

    if not where_values:
        where_values = None
    if default_settings.HAVE_KERBEROS:
        os.environ['KRB5_CONFIG'] = os.path.join(os.path.abspath(os.path.dirname(__file__)).replace("/utils", ''), 'resource/' + default_settings.env_str + '-krb5.conf')
        keytab_path = os.path.join(os.path.abspath(os.path.dirname(__file__)).replace("/utils", ''), 'resource/' + default_settings.env_str + '-hive.keytab')
        principal = default_settings.KERBEROS_DOMAIN
        with krbcontext(using_keytab=True, principal=principal, keytab_file=keytab_path):
            db = connect(host=config["host"], port=10000, database=config["db_name"], auth_mechanism='GSSAPI', use_ssl=False, kerberos_service_name='hive')
            return hive_db_operation(db, limit, sql, where_values)
    else:
        db = connect(host=config["host"], port=10000, database=config["db_name"], user=config["user"], password=config["password"], auth_mechanism='PLAIN')
        return hive_db_operation(db, limit, sql, where_values)


def hive_db_operation(db, limit, sql, where_values):
    cursor = db.cursor()
    try:
        if sql == 'show tables' or 'desc' in sql:
            cursor.execute(sql)
        else:
            cursor.execute(sql + ' limit ' + str(limit), where_values)
        result = cursor.fetchall()
        return result
    except Exception as e:
        logger.error(e)
        raise e
    finally:
        cursor.close()
        db.close()


def __es(config, sql="select 1", where_values=None, limit=1000):
    if not where_values:
        where_values = None
    if config["port"]:
        url = 'http://{}:{}/_xpack/sql?format=json'.format(config["host"], config["port"])
    else:
        url = 'http://{}/_xpack/sql?format=json'.format(config["host"])

    body = {"query": sql, "fetch_size": limit}
    if where_values:
        body["params"] = where_values
    headers = {'Content-Type': 'application/json'}
    res = requests.post(url, json=body, headers=headers)

    return res.json()['rows']


def __clickhouse(config, sql="select 1", where_values=None, limit=1000):
    if not where_values:
        where_values = []
    # db = Client(host=config["host"], db=config["db_name"], user=config["user"], password=config["password"], port=config["port"])
    db = clickhouse_driver.connect('clickhouse://' + config["user"] + ':' + config["password"] + '@' + config["host"] + ':' + config["port"] + '/' + config["db_name"])
    cursor = db.cursor()
    try:
        where_value_dict = {}
        for index, value in enumerate(where_values):
            index_ = 't' + str(index)
            where_value_dict[index_] = value
            sql = sql.replace('%s', '%(' + index_ + ')s', 1)
        if sql == 'show tables':
            cursor.execute(sql)
        else:
            if where_value_dict:
                cursor.execute(sql + ' limit ' + str(limit), where_value_dict)
            else:
                cursor.execute(sql + ' limit ' + str(limit))
        result = cursor.fetchall()
        return result
    except Exception as e:
        logger.error(e)
        raise e
    finally:
        cursor.close()
        db.close()
