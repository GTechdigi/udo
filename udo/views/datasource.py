from flask import Blueprint, current_app, request
from udo.models.Source import DatabaseSource, TableSource, FieldSource
from udo import db
from udo.JsonResult import ok, failed
from udo.utils.AEScoder import AES_Encrypt, AES_Decrypt
from udo.utils import Connection
import threading, datetime
from udo.common import UdoErrors
from udo.views.connect import connect_test
import datetime
import re

datasource = Blueprint('datasource', __name__, url_prefix='/datasource')

key = '0CoJUm6Qyw8W8jud'


@datasource.route('/add', methods=['POST'])
def add_source():
    data = request.get_json()
    db_name = data['db_name']
    status = connect_test(data)
    if status.json['data'] == 'Connect Success':
        if not data['db_name']:
            db_name = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        db_code = data['source_type'] + '_' + db_name
        new_data = DatabaseSource(
            source_type=data['source_type'],
            source_name=data['source_name'],
            host=data['host'],
            port=data['port'],
            user=data['user'],
            password=AES_Encrypt(key, data['password']),
            db_name=data['db_name'],
            db_code=db_code,
            create_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            update_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        db.session.add(new_data)
        try:
            db.session.commit()
            # add_table(data)
            app = current_app._get_current_object()
            t = threading.Thread(target=add_table, args=(app, data, db_code))
            t.start()
        except BaseException as e:
            db.session.rollback()
            return failed(UdoErrors.UdoErrors.CREATE_FAILED)
        return ok("添加成功")
    else:
        return failed(UdoErrors.UdoErrors.CONNECT_FAILED)

@datasource.route('/queryDatabases', methods=['GET'])
def query_databases():
    source_type = request.args.get('source_type')
    query_all = DatabaseSource.query.with_entities(DatabaseSource.source_type, DatabaseSource.source_name,
                                                   DatabaseSource.db_code, DatabaseSource.db_name)
    if source_type:
        query_all = query_all.filter_by(source_type=source_type)
    result = query_all.order_by(DatabaseSource.create_time.desc()).all()
    result_list = []
    for row in result:
        line = (dict(zip(['source_type', 'source_name', 'db_code', 'db_name'], row)))
        result_list.append(line)

    return ok(result_list)


@datasource.route('/queryTables', methods=['GET'])
def query_tables():
    db_code = request.args.get('db_code')
    if db_code:
        result = TableSource.query.filter_by(db_code=db_code).all()
    else:
        result = TableSource.query.all()

    return ok(result)


@datasource.route('/queryField', methods=['GET'])
def query_field():
    table_code = request.args.get('table_code')
    if table_code:
        result = FieldSource.query.filter_by(table_code=table_code).all()
    else:
        result = FieldSource.query.all()
    return ok(result)


@datasource.route('/refresh', methods=['GET'])
def refresh_table_info():
    db_code = request.args.get('db_code')
    datasource = DatabaseSource.query.filter_by(db_code=db_code).first()
    info = datasource.to_json()
    info['password'] = AES_Decrypt(key, info['password'])
    TableSource.query.filter_by(db_code=info['db_code']).delete(synchronize_session=False)
    db.session.commit()
    FieldSource.query.filter_by(db_code=info['db_code']).delete(synchronize_session=False)
    db.session.commit()
    app = current_app._get_current_object()
    t = threading.Thread(target=add_table, args=(app, info, info['db_code']))
    t.start()
    return ok("刷新成功")


def add_table(app, config, db_code):
    with app.app_context():
        if config['source_type'] in 'mysql':
            tables = Connection.__mysql(config, "show tables")
        elif config['source_type'] == 'hive':
            tables = Connection.__hive(config, 'show tables')
        elif config['source_type'] == 'es':
            tables = Connection.__es(config, 'show tables')
            # es 6版本 返回二个字段：name、type
            # es 7版本 返回四个字段：catalog、name、type、kind
            if len(tables[0]) == 4:
                for table in tables:
                    table[0] = table[1]
                    table[1] = table[3]
        elif config['source_type'] == 'clickhouse':
            tables = Connection.__clickhouse(config, 'show tables')
            print(tables)
        es_tables = set([])
        for table in tables:
            # kibana索引 和 gateway索引，有动态删除
            table_name = table[0]
            if config['source_type'] == 'es':
                table_name = re.sub('[0-9]{4}\\.[0-9]{2}\\.[0-9]{2}', '*', table_name)
                table_name = re.sub('[0-9]{4}\\-[0-9]{2}\\-[0-9]{2}', '*', table_name)
                if table_name in es_tables:
                    continue
                es_tables.add(table_name)
                if table_name != table[0]:
                    table[1] = 'ALIAS'
            table_code = db_code + '_' + table_name
            new_data = TableSource(
                source_type=config['source_type'],
                table_name=table_name,
                db_code=db_code,
                table_code=table_code)
            db.session.add(new_data)
            if config['source_type'] == 'hive':
                sql = "desc {}".format(table_name)
                colunms = Connection.__hive(config, sql)
                for colunm in colunms:
                    if colunm[0] and colunm[1] and '#' not in colunm[0]:
                        new_colunm = FieldSource(
                            source_type=config['source_type'],
                            field_name=colunm[0],
                            field_type=colunm[1],
                            db_code=db_code,
                            table_code=table_code)
                        db.session.add(new_colunm)
            elif config['source_type'] == 'mysql':
                sql = "select COLUMN_NAME,COLUMN_DEFAULT,IS_NULLABLE,COLUMN_TYPE,COLUMN_KEY,COLUMN_COMMENT" \
                      " from information_schema.columns " \
                      "where table_schema = '{}'and table_name = '{}' ".format(config['db_name'], table_name)
                colunms = Connection.__mysql(config, sql)
                for colunm in colunms:
                    new_colunm = FieldSource(
                        source_type=config['source_type'],
                        field_name=colunm[0],
                        default_value=colunm[1],
                        is_null=colunm[2],
                        field_type=colunm[3],
                        primary_key=colunm[4],
                        field_describe=colunm[5],
                        db_code=db_code,
                        table_code=table_code)
                    db.session.add(new_colunm)
            elif config['source_type'] == 'es':
                sql = "desc \"" + table_name + "\""
                colunms = Connection.__es(config, sql)
                for colunm in colunms:
                    new_colunm = FieldSource(
                        source_type=config['source_type'],
                        field_name=colunm[0],
                        field_type=colunm[1],
                        primary_key=colunm[2],
                        db_code=db_code,
                        table_code=table_code)
                    db.session.add(new_colunm)
            elif config['source_type'] == 'clickhouse':
                sql = "select COLUMN_NAME,COLUMN_DEFAULT,IS_NULLABLE,COLUMN_TYPE,COLUMN_COMMENT" \
                      " from information_schema.columns " \
                      "where table_schema = '{}'and table_name = '{}' ".format(config['db_name'], table_name)
                colunms = Connection.__clickhouse(config, sql)
                for colunm in colunms:
                    new_colunm = FieldSource(
                        source_type=config['source_type'],
                        field_name=colunm[0],
                        default_value=colunm[1],
                        is_null=colunm[2],
                        field_type=colunm[3],
                        field_describe=colunm[4],
                        db_code=db_code,
                        table_code=table_code)
                    db.session.add(new_colunm)
            db.session.commit()
