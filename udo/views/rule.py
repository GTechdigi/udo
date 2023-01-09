#encoding='utf-8'
import codecs
import datetime
import uuid
import sqlparse
import base64

from flask import Blueprint, request

from log import logger
from udo import db
from udo.JsonResult import ok, failed, ok_base_page, ok_page
from udo.common.UdoErrors import UdoErrors
from udo.models.Project import UdoProject
from udo.models.Rule import UdoRule, UdoRuleInfo, UdoRuleLog
from udo.models.Source import DatabaseSource
from udo.services import user_service, project_user_service
from udo.utils import Page
from udo.views.jobManager import delJobInfo
from udo.views.operateLog import addOperateLog

rule = Blueprint('rule', __name__, url_prefix='/rule')
Operate = {'url': '', 'type': '', 'db_code': '', 'project_code': '', 'rule_code': '', 'job_code': '', 'ip': '',
           'request_body': '', 'output': '', 'create_user': ''}


@rule.route('/add', methods=['POST'])
def addRule():
    rule_info = request.get_json()
    create_user = user_service.get_current_user(request)
    create_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rule_code = uuid.uuid4()
    add_rule(rule_code, rule_info, create_user, create_time)
    db.session.commit()
    Operate['url'] = request.path
    Operate['type'] = 'add'
    Operate['project_code'] = rule_info['project_code']
    Operate['rule_code'] = rule_code
    Operate['ip'] = request.remote_addr
    Operate['request_body'] = str(rule_info)
    Operate['output'] = ok(1)
    addOperateLog(Operate)
    return ok(1)


@rule.route('/update/<rule_code>', methods=['POST'])
def updateRule(rule_code=None):
    result = UdoRule.query.with_entities(UdoRule.create_user, UdoRule.create_time).filter(
        UdoRule.rule_code == rule_code).first()
    create_user = result['create_user']
    create_time = result['create_time']
    # deleteRule(None, rule_code)
    rule_info = request.get_json()
    UdoRuleInfo.query.filter_by(rule_code=rule_code).delete()
    UdoRule.query.filter_by(rule_code=rule_code).delete()
    add_rule(rule_code, rule_info, create_user, create_time)
    db.session.commit()
    logger.info("update 1")
    Operate['url'] = request.path
    Operate['type'] = 'update'
    Operate['rule_code'] = rule_code
    Operate['project_code'] = rule_info['project_code']
    Operate['ip'] = request.remote_addr
    Operate['request_body'] = str(rule_info)
    Operate['output'] = ok(1)
    addOperateLog(Operate)
    return ok(1)


def add_rule(rule_code, rule_info, create_user, create_time):
    update_user = user_service.get_current_user(request)
    check_db = DatabaseSource.query.filter_by(db_code=rule_info['check_db_code']).first()
    contrast_db = DatabaseSource()
    if rule_info['contrast_db_code']:
        contrast_db = DatabaseSource.query.filter_by(db_code=rule_info['contrast_db_code']).first()
    rule_description = None
    if 'rule_description' in rule_info:
        rule_description = rule_info['rule_description']
    project_code = None
    if 'project_code' in rule_info:
        project_code = rule_info['project_code']

    if 'check_table_sql' in rule_info and rule_info['check_table_sql']:
        rule_info['check_table_sql'] = str(base64.b64decode(rule_info['check_table_sql']), 'UTF-8')
    if 'contrast_table_sql' in rule_info and rule_info['contrast_table_sql']:
        rule_info['contrast_table_sql'] = str(base64.b64decode(rule_info['contrast_table_sql']), 'UTF-8')

    new_data = UdoRule(
        project_code=project_code,
        rule_code=rule_code,
        rule_name=rule_info['rule_name'],
        rule_description=rule_description,
        rule_type=rule_info['rule_type'],
        check_db_code=rule_info['check_db_code'],
        check_db_name=check_db.db_name,
        check_table_code=rule_info['check_table_code'],
        check_table_name=rule_info['check_table_name'],
        contrast_db_code=rule_info['contrast_db_code'],
        contrast_db_name=contrast_db.db_name,
        contrast_table_code=rule_info['contrast_table_code'],
        contrast_table_name=rule_info['contrast_table_name'],
        execution_cycle=rule_info['execution_cycle'],
        next_execution_time=rule_info['next_execution_time'],
        last_execution_time=rule_info['last_execution_time'],
        last_execution_status=rule_info['last_execution_status'],
        create_user=create_user,
        update_user=update_user,
        create_time=create_time,
        update_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        check_source_type=rule_info['check_source_type'],
        contrast_source_type=rule_info['contrast_source_type'],
        check_table_sql=rule_info['check_table_sql'],
        contrast_table_sql=rule_info['contrast_table_sql'],
        alert_user=','.join(rule_info['alert_user'])
    )
    db.session.add(new_data)
    field_data_list = []
    for field in rule_info['fields']:
        aggregate_type = None if 'aggregate_type' not in field else field['aggregate_type']
        field_data = UdoRuleInfo(rule_code=rule_code, col=field['field'], operator=field['operator'],
                                 aggregate_type=aggregate_type,
                                 expected_value=field['value'], expression=field['expression'],
                                 operator_type=field['operator_type'],
                                 role_information=field['role_information'])
        field_data_list.append(field_data)
    if field_data_list:
        db.session.bulk_save_objects(field_data_list)


@rule.route('/list', methods=['GET'])
def rule_list():
    project_code = request.args.get('project_code')
    rule_name = request.args.get('rule_name')
    rule_type = request.args.get('rule_type')
    page_num = int(request.args.get('page_num') or 1)
    page_size = int(request.args.get('page_size') or 10)
    project_code_list = project_user_service.query_project_code_list_by_username(user_service.get_current_user(request))
    if not project_code_list or (project_code and project_code not in project_code_list):
        return ok_page([], 0)

    query = UdoRule.query
    if project_code:
        query = query.filter_by(project_code=project_code)
    else:
        query = query.filter(UdoRule.project_code.in_(project_code_list))
    if rule_name:
        query = query.filter(UdoRule.rule_name.like('%' + rule_name + '%'))
    if rule_type:
        query = query.filter(UdoRule.rule_type == rule_type)
    query = query.order_by(UdoRule.update_time.desc())
    rule_info, total = Page.page(query, page_num, page_size)
    rule_info_list = []
    for rule_temp in rule_info:
        rule_ = rule_temp.to_json()
        if rule_['project_code']:
            projectInfo = UdoProject.query.filter(UdoProject.project_code == rule_['project_code']).first()
            if projectInfo:
                rule_['project_name'] = projectInfo.project_name
        rule_info_list.append(rule_)
    return ok_base_page(rule_info_list, total)


@rule.route('/deleteRule/<rule_code>', methods=['GET'])
def delete_rule(rule_code=None):
    try:
        # rule_code = request.args.get('rule_code')
        delJobInfo(rule_code)
        UdoRuleInfo.query.filter_by(rule_code=rule_code).delete()
        UdoRule.query.filter_by(rule_code=rule_code).delete()
        db.session.commit()
        Operate['url'] = request.path
        Operate['type'] = 'delete'
        Operate['rule_code'] = rule_code
        Operate['ip'] = request.remote_addr
        Operate['request_body'] = str(request.get_json())
        Operate['output'] = ok('删除成功')
        addOperateLog(Operate)
        return ok('删除成功')
    except BaseException as e:
        logger.error("删除规则失败", e)
        db.session.rollback()
        Operate['output'] = failed(UdoErrors.DELETE_FAILED)
        return failed(UdoErrors.DELETE_FAILED)


def delete_rule(rule_code=None):
    try:
        delJobInfo(rule_code)
        UdoRuleInfo.query.filter_by(rule_code=rule_code).delete()
        UdoRule.query.filter_by(rule_code=rule_code).delete()
        db.session.commit()
        return ok('删除成功')
    except BaseException as e:
        logger.error("删除规则失败", e)
        db.session.rollback()
        return failed(UdoErrors.DELETE_FAILED)


def deleteRule(project_code=None, rule_code=None):
    if project_code:
        try:
            rule_infos = UdoRule.query.filter_by(project_code=project_code).all()
            for rule_info in rule_infos:
                if rule_info.rule_code:
                    inner_del(rule_info.rule_code)
            return ok('删除成功')
        except BaseException as e:
            logger.error("删除规则失败", e)
            db.session.rollback()
            return failed(UdoErrors.DELETE_FAILED)
    if rule_code:
        try:
            inner_del(rule_code)
            return ok('删除成功')
        except BaseException as e:
            logger.error("删除规则失败", e)
            db.session.rollback()
            return failed(UdoErrors.DELETE_FAILED)


def inner_del(rule_code=None):
    delJobInfo(rule_code)
    UdoRuleInfo.query.filter_by(rule_code=rule_code).delete()
    UdoRule.query.filter_by(rule_code=rule_code).delete()


@rule.route('/info', methods=['GET'])
def get_rule():
    rule_code = request.args.get('rule_code')
    udo_rule = UdoRule.query.filter_by(rule_code=rule_code).first()
    udo_role_info = UdoRuleInfo.query.filter_by(rule_code=rule_code).all()
    rule_json = udo_rule.to_json()
    if rule_json['alert_user']:
        rule_json['alert_user'] = rule_json['alert_user'].split(',')
    info_list = []
    for info in udo_role_info:
        info_list.append(info.to_json())
    rule_json['fields'] = info_list
    return ok(rule_json)


@rule.route('/logList', methods=['GET'])
def queryRuleLog():
    project_code = request.args.get('project_code')
    rule_name = request.args.get("rule_name")
    rule_type = request.args.get("rule_type")
    rule_code = request.args.get("rule_code")
    page_num = int(request.args.get('page_num') or 1)
    page_size = int(request.args.get('page_size') or 10)
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    status = request.args.get("status")
    check_status = request.args.get("check_status")
    end_date_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    end_date_last = end_date_dt+datetime.timedelta(days=1)
    new_end_date = end_date_last.strftime("%Y-%m-%d")
    project_code_list = project_user_service.query_project_code_list_by_username(user_service.get_current_user(request))
    if not project_code_list or (project_code and project_code not in project_code_list):
        return ok_page([], 0)

    query = UdoRuleLog.query
    if rule_name:
        query = query.filter(UdoRuleLog.rule_name.like('%' + rule_name + '%'))
    if rule_type:
        query = query.filter_by(rule_type=rule_type)
    if rule_code:
        query = query.filter_by(rule_code=rule_code)
    if project_code:
        query = query.filter_by(project_code=project_code)
    if status:
        query = query.filter_by(status=status)
    if check_status:
        query = query.filter_by(check_status=check_status)
    else:
        query = query.filter(UdoRuleLog.project_code.in_(project_code_list))
    query = query.filter(UdoRuleLog.start_time >= start_date)
    query = query.filter(UdoRuleLog.start_time < new_end_date)
    query = query.order_by(UdoRuleLog.start_time.desc())
    rule_logs, total = Page.page(query, page_num, page_size)
    rule_log_json_list = []
    for rule_log in rule_logs:
        rule_log_json = rule_log.to_json()
        if rule_log_json['project_code']:
            project = UdoProject.query.filter_by(project_code=rule_log_json['project_code']).first()
            rule_log_json['project_name'] = project.project_name
        rule_log_json_list.append(rule_log_json)
    return ok_base_page(rule_log_json_list, total)


@rule.route('/sql/columns', methods=['POST'])
def sql_columns():
    sql_info = request.get_json()
    sql_base64 = sql_info['sql']
    if not sql_base64:
        return failed(UdoErrors.SQL_NULL_FAILED)
    logger.info("sql base64: %s", sql_base64)
    try:
        sql = str(base64.b64decode(sql_base64), 'UTF-8')
    except:
        return failed(UdoErrors.SQL_ERROR_FAILED)
    logger.info("sql : %s", sql)
    parsed = sqlparse.parse(sql)
    columns = []
    for token in parsed[0].tokens:
        if isinstance(token, sqlparse.sql.IdentifierList):
            logger.info("sql tokens : %s", token.tokens)
            for col in token.tokens:
                if isinstance(col, sqlparse.sql.Identifier):
                    # column = col.value.split(' ')[-1].strip('`').rpartition('.')[-1]
                    column = col.tokens[-1].value.strip('`').rpartition('.')[-1]
                    if column not in columns:
                        columns.append(column)
    return ok(columns)

