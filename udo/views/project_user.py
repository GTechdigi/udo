from flask import Blueprint, request

from udo.models.Project import UdoProject
from udo import db
from sqlalchemy import or_, and_
from udo.common.UdoErrors import UdoErrors
from udo.JsonResult import ok, failed, ok_base_page, ok_page
from udo.services import user_service
from udo.models.ProjectUser import UdoProjectUser
from udo.views.operateLog import addOperateLog
import datetime
from udo.utils import Page
from log import logger

log = logger
Operate = {'url': '', 'type': '', 'db_code': '', 'project_code': '', 'rule_code': '', 'job_code': '', 'ip': '',
           'request_body': '', 'output': '', 'create_user': ''}
projectUser = Blueprint('projectUser', __name__, url_prefix='/projectUser')


@projectUser.route('/add', methods=['POST'])
def addProjectUser():
    param = request.get_json()
    project_code = param['project_code']
    username = param['username']
    current_username = user_service.get_current_user(request)
    create_user = current_username
    update_user = current_username
    new_data = UdoProjectUser(
        project_code=project_code,
        username=username,
        create_user=create_user,
        update_user=update_user,
        create_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        update_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    Operate['type'] = 'add'
    Operate['url'] = request.path
    Operate['ip'] = request.remote_addr
    Operate['request_body'] = str(param)
    project_code_user = UdoProjectUser.query.filter(UdoProjectUser.project_code == project_code,
                                                    UdoProjectUser.username == username).first()
    if project_code_user:
        Operate['output'] = failed(UdoErrors.ADD_FAILED)
        addOperateLog(Operate)
        return failed(UdoErrors.ADD_FAILED)
    else:
        db.session.add(new_data)
        Operate['output'] = ok("加入成功")
        addOperateLog(Operate)
        return ok("加入成功")


@projectUser.route('/update', methods=['GET'])
def updateProjectUser():
    project_code = request.args.get('project_code')
    username = request.args.get('username')
    update_user = user_service.get_current_user(request)
    project_code_list = str(project_code).split(",")
    user_name_list = str(username).split(",")

    for project_code in project_code_list:
        for user_name in user_name_list:
            UdoProjectUser.query.filter(
                or_(UdoProjectUser.project_code == project_code, UdoProjectUser.username == user_name)).delete()
            db.session.commit()

    for project_code in project_code_list:
        for user_name in user_name_list:
            new_data = UdoProjectUser(
                project_code=project_code,
                username=user_name,
                create_user=update_user,
                update_user=update_user,
                create_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                update_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            db.session.add(new_data)
    return ok("更新成功")


@projectUser.route('/delete', methods=['GET'])
def deleteProjectUser():
    project_code = request.args.get('project_code')
    username = request.args.get('username')
    if project_code and username:
        UdoProjectUser.query.filter(UdoProjectUser.project_code == project_code) \
            .filter(UdoProjectUser.username == username).delete()
        db.session.commit()
    Operate['type'] = 'delete'
    Operate['url'] = request.path
    Operate['ip'] = request.remote_addr
    Operate['request_body'] = str(project_code)
    Operate['output'] = ok("删除完成")
    addOperateLog(Operate)
    return ok("删除完成")


@projectUser.route('/list', methods=['GET'])
def projectUserList():
    project_code = request.args.get('project_code')
    username = request.args.get('username')
    page_num = int(request.args.get('page_num') or 1)
    page_size = int(request.args.get('page_size') or 10)
    query = UdoProjectUser.query
    if project_code:
        query = query.filter(UdoProjectUser.project_code == project_code)
    if username:
        query = query.filter(UdoProjectUser.username == username)
    query = query.order_by(UdoProjectUser.update_time.desc())
    project_info, total = Page.page(query, page_num, page_size)
    rule_info_list = []
    for rule_temp in project_info:
        rule_ = rule_temp.to_json()
        if rule_['project_code']:
            projectInfo = UdoProject.query.filter(UdoProject.project_code == rule_['project_code']).first()
            if projectInfo:
                rule_['project_name'] = projectInfo.project_name
        rule_info_list.append(rule_)
    return ok_base_page(rule_info_list, total)


@projectUser.route('/info', methods=['GET'])
def getProjectUser():
    project_code = request.args.get('project_code')
    username = request.args.get('username')
    project_info = UdoProjectUser.query.filter(UdoProjectUser.project_code == project_code).filter(
        UdoProjectUser.username == username).first()
    rule_ = project_info.to_json()
    if rule_['project_code']:
        projectInfo = UdoProject.query.filter(UdoProject.project_code == rule_['project_code']).first()
        if projectInfo:
            rule_['project_name'] = projectInfo.project_name
    return ok(rule_)
