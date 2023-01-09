from flask import Blueprint, request
from sqlalchemy import or_
from udo.models.Job import UdoJobInfo, UdoJob
from udo.models.Project import UdoProject
from udo.models.Rule import UdoRule
from udo.views.run_rule import run_rule
from udo import db, scheduler
import apscheduler
from udo.views.operateLog import addOperateLog
import time
import random
from udo.utils.TimeUtils import timestamp_to_date_time
from udo.JsonResult import ok, failed, ok_page
import datetime
from udo.common.UdoErrors import UdoErrors
from udo.utils import Page
from log import logger
from udo.services import user_service, project_user_service


log = logger
job = Blueprint('job', __name__, url_prefix='/job')
Operate = {'url': '', 'type': '', 'db_code': '', 'project_code': '', 'rule_code': '', 'job_code': '', 'ip': '',
           'request_body': '', 'output': '', 'create_user': ''}


def get_next_run_time():
    jobs_info = UdoJob.query.all()
    for info in jobs_info:
        info = info.to_json()
        UdoJobInfo.query.filter_by(job_id=info['id']).update(
            {"next_run_time": timestamp_to_date_time(info['next_run_time'])})
        db.session.commit()


def add_job(job_id):
    #  job_id = request.args.get("job_id")
    jobs_info = UdoJobInfo.query.filter_by(job_id=job_id).all()
    for info in jobs_info:
        job_def = fix_job_def(info.to_json())
        scheduler.add_job(**job_def)


def delete_job(job_id):
    try:
        scheduler.remove_job(job_id)
    except:
        pass


@job.route('/changeStatus', methods=['POST'])
def chang_status_job():
    param = request.get_json()
    job_id = param['job_id']
    is_run = param['is_run']
    try:
        if job_id and is_run == 0:
            try:
                scheduler.pause_job(job_id)
            except apscheduler.jobstores.base.JobLookupError as e:
                add_job(job_id)
                scheduler.pause_job(job_id)
            UdoJobInfo.query.filter_by(job_id=job_id).update({'is_run': 0})
            db.session.commit()
        if job_id and is_run == 1:
            try:
                scheduler.resume_job(job_id)
            except apscheduler.jobstores.base.JobLookupError as e:
                add_job(job_id)
                scheduler.resume_job(job_id)
            UdoJobInfo.query.filter_by(job_id=job_id).update({'is_run': 1})
            db.session.commit()
    except IOError as e:
        log.error('changeStatus failed', e)
    Operate['type'] = 'update'
    Operate['url'] = request.path
    Operate['job_code'] = job_id
    Operate['ip'] = request.remote_addr
    Operate['request_body'] = str(param)
    Operate['output'] = ok(1)
    addOperateLog(Operate)
    return ok(1)


def fix_job_def(job_info):
    """维修job工程"""
    job_def = dict()
    job_def['id'] = job_info.get('job_id') or None
    job_def['func'] = run_rule or None
    job_def['replace_existing'] = True
    job_def['args'] = [job_info.get('rule_code'), False] or None
    job_def['trigger'] = job_info.get('trigger') or None
    if job_info.get('trigger') == 'date':
        job_def['run_date'] = job_info.get('run_date') or None
    elif job_info.get('trigger') == 'cron':
        job_def['start_date'] = job_info.get('start_date') or None
        job_def['end_date'] = job_info.get('end_date') or None
        job_def['hour'] = job_info.get('hour') or None
        job_def['second'] = job_info.get('second') or None
        job_def['minute'] = job_info.get('minute') or None
        job_def['week'] = job_info.get('week') or None
        job_def['day'] = job_info.get('day') or None
        job_def['month'] = job_info.get('month') or None
        job_def['year'] = job_info.get('year') or None
        job_def['day_of_week'] = job_info.get('day_of_week') or None
    elif job_info.get('trigger') == 'interval':
        job_def['start_date'] = job_info.get('start_date') or None
        job_def['end_date'] = job_info.get('end_date') or None
        if job_info.get('minute'):
            job_def['minutes'] = int(job_info.get('minute'))
        if job_info.get('hour'):
            job_def['hours'] = int(job_info.get('hour'))
        if job_info.get('day'):
            job_def['days'] = int(job_info.get('day'))
        if job_info.get('second'):
            job_def['seconds'] = int(job_info.get('second'))
    return job_def


@job.route('/addJob', methods=['POST'])
def addJobInfo():
    job_info = request.get_json()
    current_username = user_service.get_current_user(request)
    create_user = current_username
    update_user = current_username
    job_id = str(int(time.time() * 1000)) + str(random.randint(10000, 99999))
    project_code = None
    if 'project_code' in job_info:
        project_code = job_info['project_code']
    is_run = None
    if 'is_run' in job_info:
        is_run = job_info['is_run']
    new_job = UdoJobInfo(
        job_id=job_id,
        job_name=job_info['job_name'],
        project_code=project_code,
        rule_code=','.join(job_info['rule_code']),
        trigger=job_info['trigger'],
        run_date=job_info['run_date'],
        start_date=job_info['start_date'],
        end_date=job_info['end_date'],
        year=job_info['year'],
        month=job_info['month'],
        day=job_info['day'],
        day_of_week=job_info['day_of_week'],
        hour=job_info['hour'],
        minute=job_info['minute'],
        second=job_info['second'],
        status=job_info['status'],
        create_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        update_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        create_user=create_user,
        update_user=update_user,
        is_run=is_run
    )
    db.session.add(new_job)
    db.session.commit()
    add_job(job_id)
    Operate['url'] = request.path
    Operate['type'] = 'add'
    Operate['project_code'] = job_info['project_code']
    Operate['rule_code'] = ','.join(job_info['rule_code'])
    Operate['job_code'] = job_id
    Operate['ip'] = request.remote_addr
    Operate['request_body'] = str(job_info)
    Operate['output'] = ok("添加成功")
    addOperateLog(Operate)
    return ok("添加成功")


@job.route('/delJob', methods=['GET'])
def delJob():
    try:
        current_username = user_service.get_current_user(request)
        update_user = current_username
        job_id = request.args.get('job_id')
        job_info = UdoJobInfo.query.filter_by(job_id=job_id).first()
        job_info.status = 2
        job_info.update_user = update_user
        job_info.update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        delete_job(job_info.job_id)
        db.session.commit()
        Operate['url'] = request.path
        Operate['type'] = 'delete'
        Operate['job_code'] = job_id
        Operate['ip'] = request.remote_addr
        Operate['request_body'] = str(job_id)
        Operate['output'] = ok("删除完成")
        addOperateLog(Operate)
        return ok("删除完成")
    except BaseException as e:
        log.error("删除任务失败", e)
        db.session.rollback()
        return failed(UdoErrors.NO_JOB)


def delJobInfo(rule_code=None):
    job_infos = UdoJobInfo.query.filter_by(rule_code=rule_code, status=1).all()
    current_username = user_service.get_current_user(request)
    update_user = current_username
    for job_info in job_infos:
        job_info.status = 2
        job_info.update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        job_info.update_user = update_user
        try:
            delete_job(job_info.job_id)
        except BaseException as e:
            log.error("删除任务失败", e)
            continue
    return ok("删除完成")


@job.route('/queryJob', methods=['GET'])
def queryJobInfo():
    get_next_run_time()
    project_code = request.args.get('project_code')
    job_name = request.args.get('job_name')
    rule_name = request.args.get('rule_name')
    trigger = request.args.get('trigger')
    page_num = int(request.args.get('page_num') or 1)
    page_size = int(request.args.get('page_size') or 10)
    project_code_list = project_user_service.query_project_code_list_by_username(user_service.get_current_user(request))
    if not project_code_list or (project_code and project_code not in project_code_list):
        return ok_page([], 0)

    query = UdoJobInfo.query
    if job_name:
        query = query.filter(UdoJobInfo.job_name.like('%' + job_name + '%'))
    if trigger:
        query = query.filter_by(trigger=trigger)
    if project_code:
        query = query.filter_by(project_code=project_code)
    else:
        query = query.filter(UdoJobInfo.project_code.in_(project_code_list))

    query = query.filter_by(status=1).filter(
        or_(UdoJobInfo.run_date >= datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            UdoJobInfo.trigger != 'date')).order_by(UdoJobInfo.update_time.desc())
    job_info, total = Page.page(query, page_num, page_size)
    info_list = []
    for info in job_info:
        info_json = info.to_json()
        rule_code = info_json['rule_code'].split(',')
        info_json['rule_name'] = ''
        for i in rule_code:
            udo_rule = UdoRule.query.filter_by(rule_code=i).first()
            if udo_rule:
                rule_json = udo_rule.to_json()
                if rule_name and rule_name not in rule_json['rule_name']:
                    continue
                if rule_code.index(i) != 0:
                    info_json['rule_name'] += ',' + rule_json['rule_name']
                else:
                    info_json['rule_name'] += rule_json['rule_name']

        if info_json['project_code']:
            projectInfo = UdoProject.query.filter(UdoProject.project_code == info_json['project_code']).first()
            if projectInfo:
                info_json['project_name'] = projectInfo.project_name
        info_list.append(info_json)
    return ok_page(info_list, total)


@job.route('/updateJobInfo/<job_id>', methods=['POST'])
def updateJobInfo(job_id=None):
    if job_id is None:
        return failed(UdoErrors.NO_JOB)
    job_info = request.get_json()
    result = UdoJobInfo.query.with_entities(UdoJobInfo.create_user, UdoJobInfo.create_time).filter(
        UdoJobInfo.job_id == job_id).first()
    create_user = result['create_user']
    create_time = result['create_time']
    current_username = user_service.get_current_user(request)
    update_user = current_username
    UdoJobInfo.query.filter_by(job_id=job_id).delete()
    new_job = UdoJobInfo(
        job_id=job_id,
        job_name=job_info['job_name'],
        project_code=job_info['project_code'],
        rule_code=','.join(job_info['rule_code']),
        trigger=job_info['trigger'],
        run_date=job_info['run_date'],
        start_date=job_info['start_date'],
        end_date=job_info['end_date'],
        year=job_info['year'],
        month=job_info['month'],
        day=job_info['day'],
        day_of_week=job_info['day_of_week'],
        hour=job_info['hour'],
        minute=job_info['minute'],
        second=job_info['second'],
        status=job_info['status'],
        create_time=create_time,
        update_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        create_user=create_user,
        update_user=update_user
    )
    db.session.add(new_job)
    db.session.commit()
    add_job(job_id)
    Operate['url'] = request.path
    Operate['type'] = 'update'
    Operate['project_code'] = job_info['project_code']
    Operate['rule_code'] = ','.join(job_info['rule_code'])
    Operate['job_code'] = job_id
    Operate['ip'] = request.remote_addr
    Operate['request_body'] = str(job_info)
    Operate['output'] = ok("更新成功")
    addOperateLog(Operate)
    return ok("更新成功")


@job.route('/info/<job_id>', methods=['GET'])
def getJobInfo(job_id=None):
    job_info = UdoJobInfo.query.filter_by(job_id=job_id).first()
    job_json = job_info.to_json()
    job_json['rule_code'] = job_json['rule_code'].split(',')
    job_json['rule_name'] = ''
    for i in job_json['rule_code']:
        rule = UdoRule.query.filter_by(rule_code=i).first()
        if rule:
            rule_json = rule.to_json()
            if job_json['rule_code'].index(i) != 0:
                job_json['rule_name'] += ','+rule_json['rule_name']
            else:
                job_json['rule_name'] += rule_json['rule_name']

    return ok(job_json)
