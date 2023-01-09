from flask import Blueprint, current_app, request
from log import logger

from udo.common.UdoErrors import UdoErrors
from udo.JsonResult import ok, failed
from udo.utils import Connection
from udo import db

connect = Blueprint('connect', __name__, url_prefix='/connect')


@connect.route('/test', methods=['POST'])
def connect_test(data=None):
    if data == None:
        data = request.get_json()
    try:
        if data['source_type'] == 'mysql':
            if Connection.__mysql(data):
                return ok("Connect Success")
        elif data['source_type'] == 'hive':
            hive = Connection.__hive(data)
            logger.info(hive)
            return ok("Connect Success")
        elif data['source_type'] == 'es':
            if Connection.__es(data):
                return ok("Connect Success")
        elif data['source_type'] == 'clickhouse':
            if Connection.__clickhouse(data):
                return ok("Connect Success")
    except Exception as e:
        db.session.rollback()
        logger.error(e)
    return failed(UdoErrors.CONNECT_FAILED)


@connect.route('/test2', methods=['GET'])
def test():
    logger.info("131jfadfafa")
    logger.error("131jfadfafa")
    # db1 = pymysql.connect(host='172.19.109.55', user='gtech-dev', password='gtech-dev', db='dev_udo_db')
    # cursor = db1.cursor()
    # return send(title='测试', to_list=['li_08156759@163.com'], body='你好呀内容发送')
    # cursor.execute('select * from udo_rule where create_time > date_sub(now(),interval 1 day) ')
    # tables = cursor.fetchall()
    # return tables
    return 'ok'
