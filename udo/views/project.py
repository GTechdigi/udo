import uuid
from flask import Blueprint, request
from udo.models.Project import UdoProject
from udo import db
from udo.common.UdoErrors import UdoErrors
from udo.JsonResult import ok, failed, ok_base_page, ok_page
from udo.services import user_service, project_user_service
from udo.views.rule import deleteRule
from udo.views.operateLog import addOperateLog
from udo.models.ProjectUser import UdoProjectUser
import datetime
from udo.utils import Page
from log import logger

log = logger

project = Blueprint('project', __name__, url_prefix='/project')
Operate = {'url': '', 'type': '', 'db_code': '', 'project_code': '', 'rule_code': '', 'job_code': '', 'ip': '',
           'request_body': '', 'output': '', 'create_user': ''}


@project.route('/add', methods=['POST'])
def addProject():
    project_info = request.get_json()
    project_code = uuid.uuid4()
    first = UdoProject.query.filter_by(project_name=project_info['project_name']).first()
    if first:
        return failed(UdoErrors.ADD_PROJECT_FAILED)
    add_project(project_code, project_info)
    Operate['url'] = request.path
    Operate['type'] = 'add'
    Operate['project_code'] = project_code
    Operate['ip'] = request.remote_addr
    Operate['request_body'] = str(project_info)
    Operate['output'] = ok(1)
    current_username = user_service.get_current_user(request)
    project_user = UdoProjectUser(
        project_code=project_code,
        username=current_username,
        create_user=current_username,
        update_user=current_username,
        create_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        update_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    db.session.add(project_user)
    addOperateLog(Operate)
    return ok(1)


@project.route('/update/<project_code>', methods=['POST'])
def updateRule(project_code=None):
    project_info = request.get_json()
    update_user = user_service.get_current_user(request)
    UdoProject.query.filter_by(project_code=project_code).update(
        {'project_name': project_info['project_name'], 'project_description': project_info['project_description'],
         'we_work_robot': project_info['we_work_robot'],
         'update_user': update_user, 'update_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    db.session.commit()
    Operate['url'] = request.path
    Operate['type'] = 'update'
    Operate['project_code'] = project_info['project_code']
    Operate['ip'] = request.remote_addr
    Operate['request_body'] = str(project_info)
    Operate['output'] = ok("更新成功")
    addOperateLog(Operate)
    return ok("更新成功")


@project.route('/delProject', methods=['GET'])
def delProject():
    try:
        current_username = user_service.get_current_user(request)
        create_user = current_username
        update_user = current_username
        project_code = request.args.get('project_code')
        project_info = UdoProject.query.filter_by(project_code=project_code).first()
        project_info.is_delete = "1"
        project_info.create_user = create_user
        project_info.update_user = update_user
        project_info.update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        deleteRule(project_code)
        UdoProjectUser.query.filter_by(project_code=project_code).delete()
        db.session.commit()
        Operate['url'] = request.path
        Operate['type'] = 'delete'
        Operate['project_code'] = project_code
        Operate['ip'] = request.remote_addr
        Operate['request_body'] = str(request.get_json())
        Operate['output'] = ok("删除完成")
        addOperateLog(Operate)
        return ok("删除完成")
    except BaseException as e:
        log.error("删除任务失败", e)
        db.session.rollback()
        return failed(UdoErrors.NO_JOB)


@project.route('/list', methods=['GET'])
def projectList():
    project_name = request.args.get('project_name')
    project_description = request.args.get('project_description')
    page_num = int(request.args.get('page_num') or 1)
    page_size = int(request.args.get('page_size') or 10)

    project_code_list = project_user_service.query_project_code_list_by_username(user_service.get_current_user(request))
    if not project_code_list:
        return ok_page([], 0)

    query = UdoProject.query
    if project_name:
        query = query.filter(UdoProject.project_name.like('%' + project_name + '%'))
    if project_description:
        query = query.filter(UdoProject.project_description.like('%' + project_description + '%'))
    query = query.filter(UdoProject.project_code.in_(project_code_list)).filter_by(is_delete='0').order_by(UdoProject.update_time.desc())
    project_info, total = Page.page(query, page_num, page_size)
    return ok_base_page(project_info, total)


@project.route('/<project_code>', methods=['GET'])
def getProject(project_code=None):
    project_info = UdoProject.query.filter(UdoProject.project_code == project_code).first()
    return ok(project_info)


def add_project(project_code, project_info):
    current_username = user_service.get_current_user(request)
    create_user = current_username
    update_user = current_username
    new_data = UdoProject(
        project_code=project_code,
        project_name=project_info['project_name'],
        project_description=project_info['project_description'],
        create_user=create_user,
        update_user=update_user,
        create_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        update_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        is_delete='0',
        we_work_robot=project_info['we_work_robot']
    )
    db.session.add(new_data)


def delete_project(project_code=None):
    project_infos = UdoProject.query.filter_by(project_code=project_code, is_delete=0).all()
    current_username = user_service.get_current_user(request)
    create_user = current_username
    update_user = current_username
    for project_info in project_infos:
        project_info.is_delete = '1'
        project_info.update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        project_info.create_user = create_user
        project_info.update_user = update_user
        try:
            deleteRule(project_info.project_code, None)
        except BaseException as e:
            log.error("删除任务失败", e)
            continue
    db.session.commit()
    return ok("删除完成")
