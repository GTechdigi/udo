#coding=utf-8
import threading

from flask import Blueprint, current_app, request
import codecs
from udo.models.User import User
from udo.models.Project import UdoProject
from udo.models.ProjectUser import UdoProjectUser
from udo.models.Rule import UdoRule, UdoRuleInfo, UdoRuleLog
from udo.JsonResult import ok, failed
from udo import scheduler
from udo import db, redis
from udo.common.WxRebot import push_message
from udo.common.Message import send_email
from udo.utils.DataContrast import data_contrast
import datetime
import uuid
from log import logger
from itertools import groupby
from udo.default_settings import env_str
from udo import default_settings
from udo.views.operateLog import addOperateLog
from udo.common.OSS import upload
from udo.common.Excel import writer_excel
import re
# 勿删 因es7.0以下版本不支持sql的日期函数, 使用python eval方法执行python日期函数替换
import time

runRule = Blueprint('runRule', __name__, url_prefix='/runRule')
Operate = {'url': '', 'type': '', 'db_code': '', 'project_code': '', 'rule_code': '', 'job_code': '', 'ip': '',
           'request_body': '', 'output': '', 'create_user': ''}


@runRule.route('/runRule/<rule_code>', methods=['GET'])
def run_rule(rule_code=None, once=True):
    redis_result = True
    if not once:
        # 当获取不到分布式锁，会返回None
        redis_result = redis.set('udo:rule:' + rule_code, str(uuid.uuid1()), ex=2, nx=True)
    if redis_result:
        with scheduler.app.app_context():
            t = threading.Thread(target=run_rule_thread, args=(current_app._get_current_object(), rule_code))
            t.start()
            Operate['url'] = request.path
            Operate['type'] = 'run'
            Operate['rule_code'] = rule_code
            Operate['ip'] = request.remote_addr
            Operate['request_body'] = str(request.json)
            Operate['output'] = ok('1')
            addOperateLog(Operate)
            return ok("执行结束")


def run_rule_thread(app, rule_code):
    rule_code_list = str(rule_code).split(",")
    with app.app_context():
        error_message_tmp = ''
        for rule_code in rule_code_list:
            status = 3
            # 添加规则执行日志
            rule, rule_log = add_rule_log(rule_code, status)
            check_status = None
            project = UdoProject.query.filter_by(project_code=rule['project_code']).first()
            rule_type_name = get_rule_type_name(rule)
            content = '{} - 开始执行項目【{}】的规则：{}，规则类型：{}\n'.format(get_current_time(), project.project_name,
                                                               rule['rule_name'], rule_type_name)
            try:
                # 生成sql
                check_sql_list, contrast_sql_list, check_group_by_list, contrast_group_by_list, check_name_list,  \
                contrast_name_list, check_where_values, contrast_where_values, count_operate, expected_value \
                    = build_sql(rule)
                check_sql_result_list, content = query(check_sql_list, check_where_values, content, rule, 1)
                contrast_sql_result_list, content = query(contrast_sql_list, contrast_where_values, content, rule, 2)

                error_message = None
                if rule['rule_type'] == 'count':
                    content, error_message, error_message2 = handler_count(check_sql_result_list, count_operate,
                                                                           expected_value, content, rule, project)

                elif rule['rule_type'] == 'check_count':
                    content, error_message, error_message2 = handler_check_count(check_sql_result_list,
                                                                                 contrast_sql_result_list, content,
                                                                                 rule, project)

                elif rule['rule_type'] == 'consistency':
                    content, error_message, error_message2 = handler_consistency(check_sql_result_list,
                                                                                 contrast_sql_result_list,
                                                                                 check_name_list,
                                                                                 contrast_name_list,
                                                                                 content,
                                                                                 rule, project, check_group_by_list,
                                                                                 contrast_group_by_list)
                elif rule['rule_type'] == 'business_monitoring':
                    content, error_message, error_message2 = handler_business_monitoring(check_sql_result_list,
                                                                                         check_name_list, content,
                                                                                         rule, project)
                check_status = 1
                status = 1
            except:
                status = 2
                import traceback, sys
                traceback.print_exc()  # 打印异常信息

                exc_type, exc_value, exc_traceback = sys.exc_info()
                exception = traceback.format_exception(exc_type, exc_value, exc_traceback)

                for e in exception:
                    content += str(e)
                error_message = '【{}】<font color=\"warning\">异常</font> \n>  规则说明:<font color=\"comment\">{}</font>\n>'.format(
                    rule['rule_name'], rule['rule_description'])
                error_message2 = '【{}】异常 \n  规则说明:{}'.format(rule['rule_name'], rule['rule_description'])
                logger.error(content)

            if error_message and rule['rule_type'] != 'business_monitoring':
                check_status = 2
                content += '\n' + error_message2
            rule_log.content = content
            rule_log.status = status
            rule_log.check_status = check_status
            rule_log.end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            db.session.commit()
            error_message_tmp = error_message_tmp + error_message + '\n\n'
        alert_list = []
        if rule['alert_user']:
            alert_list = rule['alert_user'].split(',')
        push_message(message=error_message_tmp, we_work_robot=project.we_work_robot, alert_list=alert_list)
        return ok('1')


def query(sql_list, where_values, content, rule, type):
    temp = "对比"
    db_code = rule['contrast_db_code']
    if type == 1:
        temp = "校验"
        db_code = rule['check_db_code']

    sql_result_list = []
    for sql in sql_list:
        log_sql = '{} - 规则执行的{}sql：{}, 参数：{}\n'.format(get_current_time(), temp, sql, ','.join(where_values))
        logger.info(log_sql)
        content += log_sql
        sql_result = data_contrast(db_code, sql, where_values)
        if sql_result:
            sql_result = list(sql_result)
            for index, res in enumerate(sql_result):
                sql_result[index] = [str(x) if x is not None else '' for x in res]
        else:
            continue
        content += '{} - 规则执行的{}sql结果（前100条）：\n'.format(get_current_time(), temp)
        for sql_result_temp in sql_result[0: 100]:
            content += '{}\n'.format(sql_result_temp)
        sql_result_list.append(sql_result)
    return sql_result_list, content


def get_rule_type_name(rule):
    rule_type_name = None
    if rule['rule_type'] == 'count':
        rule_type_name = '数据及时性'
    elif rule['rule_type'] == 'check_count':
        rule_type_name = '数据同步'
    elif rule['rule_type'] == 'consistency':
        rule_type_name = '数据一致性'
    elif rule['rule_type'] == 'business_monitoring':
        rule_type_name = '业务监控'
    return rule_type_name


def handler_email(project, rule, columns, field_values, download_url=None, rule_time=None, file_name=None, data_size=None):
    project_user_list = UdoProjectUser.query.filter(UdoProjectUser.project_code == project.project_code).all()
    emails = []
    usernames = []
    for project_user in project_user_list:
        usernames.append(project_user.username)
    for user in User.query.filter(User.username.in_(usernames)).all():
        emails.append(user.email)
    event_code = 'UDO001'
    subject = rule['rule_name']
    if download_url:
        event_code = 'UDO002'
        subject = rule['rule_name'] + ' ' + rule_time
    email_body = {
        'domainCode': 'DC0005',
        'tenantCode': '800002',
        'orgCode': rule['rule_code'],
        'eventCode': event_code,
        'param': {
            'subject': subject,
            'emails': emails,
            'projectName': project.project_name,
            'ruleName': rule['rule_name'],
            'columns': columns,
            'fieldValues': field_values,
            'dataSize': data_size,
            'ruleTime': rule_time,
            'fileName': file_name,
            'downloadUrl': download_url
        }
    }
    send_email(email_body)


def handler_consistency(check_sql_result_list, contrast_sql_result_list, check_name_list, contrast_name_list, content,
                        rule, project, check_group_by_list, contrast_group_by_list):
    error_message = ''
    error_message2 = ''
    group_dict = {}
    col_name_list = check_name_list + check_group_by_list + contrast_name_list + contrast_group_by_list
    # 处理要输出的错误信息
    if not check_sql_result_list and not contrast_sql_result_list:
        content += '{} - 结果：\n 全部为空\n'.format(get_current_time())
        return content, error_message, error_message2
    if not check_sql_result_list:
        error_message = '【{}-{}-{}】<font color=\"warning\">异常</font> \n>规则说明:<font color=\"comment\">{}</font>\n> 校验方无数据！'.format(
            env_str, project.project_name, rule['rule_name'], rule['rule_description'])
        error_message2 = '【{}-{}-{}】异常 \n 规则说明:{}\n> 校验方无数据！'.format(env_str, project.project_name, rule['rule_name'], rule['rule_description'])
        return content, error_message, error_message2
    elif not contrast_sql_result_list:
        error_message = '【{}-{}-{}】<font color=\"warning\">异常</font> \n>规则说明:<font color=\"comment\">{}</font>\n>对比方无数据！'.format(
            env_str, project.project_name, rule['rule_name'], rule['rule_description'])
        error_message2 = '【{}-{}-{}】 异常<\n 规则说明:{}\n 对比方无数据！'.format(env_str, project.project_name, rule['rule_name'], rule['rule_description'])
        return content, error_message, error_message2
    else:
        # 按维度逐条判断是否数据一致
        group_by_list = []
        check_col_size = len(check_name_list) + len(check_group_by_list)
        contrast_col_size = len(contrast_name_list) + len(contrast_group_by_list)
        for check_sql_result in check_sql_result_list:
            group_by = ''
            sql_result = check_sql_result[0]
            for group_by_value in sql_result[-len(check_group_by_list):]:
                group_by += str(group_by_value) + '-'
            group_by_list.append(group_by)
            group_dict[group_by] = list(sql_result) + ['N/A'] * contrast_col_size

        is_error = False
        for contrast_sql_result in contrast_sql_result_list:
            group_by = ''
            sql_result = contrast_sql_result[0]
            for group_by_value in sql_result[-len(contrast_group_by_list):]:
                group_by += str(group_by_value) + '-'
            contrast_list = list(sql_result)
            if group_by not in group_by_list:
                is_error = True
                group_dict[group_by] = ['N/A'] * check_col_size + contrast_list
            else:
                check_list = group_dict[group_by][0: len(check_name_list)]
                group_dict[group_by] = group_dict[group_by][0: check_col_size] + contrast_list
                for check_index, check_field_value in enumerate(check_list):
                    if float(check_field_value) != float(contrast_list[check_index]):
                        is_error = True
        # 处理要输出的错误信息
        if is_error:
            error_message = '【{}-{}-{}】<font color=\"warning\">异常</font> \n>  规则说明:<font color=\"comment\">{}</font>\n> 请查看日志！'.format(
                env_str, project.project_name, rule['rule_name'], rule['rule_description'])
            error_message2 = '【{}-{}-{}】异常 \n 规则说明:{}\n 请查看日志！'.format(env_str, project.project_name,
                                                                       rule['rule_name'], rule['rule_description'])
            field_values = []
            for k in group_dict.keys():
                field_values.append(group_dict[k])

            handler_email(project, rule, col_name_list, field_values)
    content += '{} - 结果：\n {}\n'.format(get_current_time(), col_name_list)
    for k in group_dict.keys():
        content += '{} - {}\n'.format(get_current_time(), group_dict[k])

    return content, error_message, error_message2


def handler_check_count(check_sql_result_list, contrast_sql_result_list, content, rule, project):
    check_sql_value = 0
    contrast_sql_value = 0
    if check_sql_result_list:
        for check_sql_result in check_sql_result_list:
            check_sql_value += 0 if check_sql_result is None else int(check_sql_result[0][0])

    if contrast_sql_result_list:
        for contrast_sql_result in contrast_sql_result_list:
            contrast_sql_value += 0 if contrast_sql_result is None else int(contrast_sql_result[0][0])

    error_message = ''
    error_message2 = ''
    content += '{} - 校验记录数：{} \n 对比记录数：{}'.format(get_current_time(), check_sql_value, contrast_sql_value)
    if int(contrast_sql_value) != int(check_sql_value):
        # 处理要输出的错误信息
        error_message = '【{}-{}-{}】<font color=\"warning\">异常</font> \n>  规则说明:<font color=\"comment\">{}</font>\n> 校验记录数：<font color=\"comment\">{}</font>\n>对比记录数：<font color=\"comment\">{}</font>'.format(
            env_str, project.project_name, rule['rule_name'], rule['rule_description'], check_sql_value,
            contrast_sql_value)
        error_message2 = '【{}-{}-{}】异常 \n 规则说明: {}\n 校验记录数：{}\n 对比记录数：{}'.format(env_str,
                                                                                 project.project_name,
                                                                                 rule['rule_name'],
                                                                                 rule['rule_description'],
                                                                                 check_sql_value, contrast_sql_value)
        handler_email(project, rule, ['校验记录数', '对比记录数'], [[check_sql_value, contrast_sql_value]])
    return content, error_message, error_message2


def handler_business_monitoring(sql_result_list, field_name_list, content, rule, project):
    error_message = ''
    error_message2 = ''
    # 处理要输出的业务数据信息
    if sql_result_list and sql_result_list[0]:
        rule_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file_name = rule['rule_name'] + '_' + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '.xlsx'
        excel_path = writer_excel(sql_result_list[0], field_name_list, file_name)
        # 上传文件到oss
        download_url = upload(file_name, excel_path)
        # 发送业务数据邮件
        handler_email(project, rule, field_name_list, sql_result_list[0][0: int(default_settings.EMAIL_CONTENT_ROW)], download_url, rule_time, file_name, len(sql_result_list[0]))
        # 要发送到日志和企业微信的信息
        error_message = '【{}-{}-{}】<font color=\"warning\">完成</font> \n> 规则说明:<font color=\"comment\">{}</font>\n> 总记录数:<font color=\"comment\">{}</font>\n> 附件下载：<font color=\"comment\">[{}]({})</font>\n>'.format(
            env_str, project.project_name, rule['rule_name'], rule['rule_description'], len(sql_result_list[0]), file_name, download_url)
        content += error_message
    return content, error_message, error_message2


def handler_count(sql_result_list, count_operate, expected_value, content, rule, project):
    sql_value = 0
    if sql_result_list:
        for sql_result in sql_result_list:
            sql_value += 0 if sql_result is None else int(sql_result[0][0])
    temp = '小'
    error_message = ''
    error_message2 = ''
    if count_operate == '>=':
        err = int(expected_value) > int(sql_value)
    else:
        temp = '大'
        err = int(expected_value) < int(sql_value)
    content += '{} - 期望最{}记录数：{}\n 实际记录数: {}'.format(
        get_current_time(), temp,
        expected_value, sql_value)
    if err:
        # 处理要输出的错误信息
        error_message = '【{}-{}-{}】<font color=\"warning\">异常</font> \n> 规则说明:<font color=\"comment\">{}</font>\n> 期望最{}记录数：<font color=\"comment\">{}</font>\n>实际记录数：<font color=\"comment\">{}</font>'.format(
            env_str, project.project_name, rule['rule_name'], rule['rule_description'], temp, expected_value,
            sql_value)
        error_message2 = '【{}-{}-{}】异常 \n 规则说明: {}\n 期望最{}记录数：{}\n 实际记录数：{}'.format(env_str,
                                                                                    project.project_name,
                                                                                    rule['rule_name'],
                                                                                    rule['rule_description'], temp,
                                                                                    expected_value, sql_value)
        handler_email(project, rule, ['期望最{}记录数'.format(temp), '实际记录数'], [[expected_value, sql_value]])
    return content, error_message, error_message2


def get_current_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def build_sql(rule):
    info_data = UdoRuleInfo.query.filter_by(rule_code=rule['rule_code']).all()
    info_list = []
    check_name_list = []
    contrast_name_list = []
    check_group_by_list = []
    contrast_group_by_list = []
    check_where_values = []
    contrast_where_values = []
    count_operate = '>='
    expected_value = None
    check_sql_list = []
    contrast_sql_list = []
    for info_ in info_data:
        info_list.append(info_.to_json())

    info_list.sort(key=lambda k: (str(k.get('role_information')) + str(k.get('operator_type'))))
    for role_information, group in groupby(info_list, lambda k: (str(k.get('role_information')))):
        # role_information 1：原始表 2：对比表； operator_type 1：查询字段 2：过滤字段 3：维度字段
        if role_information == '1':
            info_type = '（原始）'
            if rule['rule_type'] == 'business_monitoring':
                info_type = ''
            check_sql_list, check_group_by_list, check_name_list, check_where_values, count_operate, expected_value \
                = build_sql_temp(info_type, group, rule['check_table_name'], rule['check_table_sql'],
                                 rule['check_source_type'])
        else:
            info_type = '（对比）'
            contrast_sql_list, contrast_group_by_list, contrast_name_list, contrast_where_values, count_operate, expected_value \
                = build_sql_temp(info_type, group, rule['contrast_table_name'], rule['contrast_table_sql'],
                                 rule['contrast_source_type'])
    return check_sql_list, contrast_sql_list, check_group_by_list, contrast_group_by_list, check_name_list, \
                contrast_name_list, check_where_values, contrast_where_values, count_operate, expected_value


def build_sql_temp(info_type, group, table_name, table_sql, source_type):
    sql_list = []
    sql_template = 'select {} from {} udo_run where 1 = 1 {}'
    columns = []
    group_by_list = []
    where_values = []
    where = ''
    count_operate = None
    expected_value = None
    placeholder = ' %s '
    if source_type == 'es':
        placeholder = ' ? '
    col_name_list = []
    for info in group:
        if info['operator_type'] == '1':
            col_name_list.append(info_type + info['col'])
            if 'sum' == info['aggregate_type']:
                columns.append('sum(' + info['col'] + ')')
            elif 'count' == info['aggregate_type']:
                columns.append('count(' + info['col'] + ')')
            else:
                columns.append(info['col'])
            count_operate = info['operator']
            expected_value = info['expected_value']
        if info['operator_type'] == '3':
            columns.append(info['col'])
            group_by_list.append(info['col'])
        if info['operator_type'] == '2':
            if info['expression'] == 1:
                where += 'and ' + info['col'] + ' ' + info['operator'] + ' ' + info['expected_value'] + ' '
            elif info['expression'] == 2:
                where_values.append(eval(info['expected_value']))
                where += 'and ' + info['col'] + ' ' + info['operator'] + placeholder
            else:

                if info['operator'] == 'in':
                    split = info['expected_value'].split(',')
                    for in_value in split:
                        where_values.append(in_value)
                    where += 'and ' + info['col'] + ' ' + info['operator'] + ' ( '+(','.join([placeholder]*len(split))) + ' ) '
                else:
                    where_values.append(info['expected_value'])
                    where += 'and ' + info['col'] + ' ' + info['operator'] + placeholder
    table_list = [table_sql]
    if table_name:
        table_list = table_name.split(",")
    for table_name_ in table_list:
        if source_type == 'es' and table_name:
            table_name_ = '"' + table_name_ + '"'
        if 'select' in table_name_.lower():
            table_name_ = '( ' + table_name_ + ' )'
        sql = sql_template.format(','.join(columns), table_name_, where)
        if group_by_list:
            sql += ' group by ' + ','.join(group_by_list)
        sql = re.sub("\n", " ", sql)
        sql = re.sub("\t", " ", sql)
        # sql = codecs.decode(sql, 'unicode_escape')
        sql = re.sub(r'(\\u[a-zA-Z0-9]{4})', lambda x: codecs.decode(x, 'unicode_escape'), sql)
        sql_list.append(sql)
    return sql_list, group_by_list, col_name_list, where_values, count_operate, expected_value


def add_rule_log(rule_code, status):
    data = UdoRule.query.filter_by(rule_code=rule_code).first()
    rule = data.to_json()
    rule_log = UdoRuleLog(
        project_code=data.project_code,
        rule_code=rule_code,
        rule_name=rule['rule_name'],
        rule_description=rule['rule_description'],
        rule_type=rule['rule_type'],
        start_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        status=status)
    db.session.add(rule_log)
    db.session.commit()
    return rule, rule_log
