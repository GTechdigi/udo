import datetime

from flask import Blueprint, current_app, request
from sqlalchemy import and_, func, false

from udo.models.Job import UdoJobInfo
from udo.models.Project import UdoProject
from udo.models.Rule import UdoRule, UdoRuleLog
from udo.JsonResult import ok

dashboard = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard.route('/projectCount', methods=['GET'])
def project_count():
    result = UdoProject.query.filter(UdoProject.is_delete != 1).count()
    return ok(result)


@dashboard.route('/jobCount', methods=['GET'])
def job_count():
    result = UdoJobInfo.query.filter(UdoJobInfo.status != 2).count()
    return ok(result)


@dashboard.route('/ruleCount', methods=['GET'])
def rule_count():
    result = UdoRule.query.count()
    return ok(result)


@dashboard.route('/ruleYesterdaySuccessCount', methods=['GET'])
def rule_yesterday_success_count():
    result = UdoRuleLog.query.filter(
        and_(UdoRuleLog.check_status == 1,
             UdoRuleLog.start_time > datetime.date.today() - datetime.timedelta(days=1),
             UdoRuleLog.end_time < datetime.date.today())).count()
    return ok(result)


@dashboard.route('/ruleYesterdayFailCount', methods=['GET'])
def rule_yesterday_fail_count():
    result = UdoRuleLog.query.filter(
        and_(UdoRuleLog.check_status != 1,
             UdoRuleLog.start_time > datetime.date.today() - datetime.timedelta(days=1),
             UdoRuleLog.end_time < datetime.date.today())).count()
    return ok(result)


@dashboard.route('/projectRuleCount', methods=['GET'])
def project_rule_count():
    result = UdoRule.query.with_entities(UdoRule.project_code, func.count(1)).group_by(UdoRule.project_code).all()
    result_list = []
    for (project_code, num) in result:
        if project_code:
            udoProject = UdoProject.query.filter(UdoProject.project_code == project_code).first()
            if udoProject:
                step = {"name": udoProject.project_name, "value": num}
                result_list.append(step)
    return ok(result_list)


@dashboard.route('/projectJobCount', methods=['GET'])
def project_job_count():
    result = UdoJobInfo.query.with_entities(UdoJobInfo.project_code, func.count(1)).group_by(UdoJobInfo.project_code).all()
    result_list = []
    for (project_code, num) in result:
        if project_code:
            udoProject = UdoProject.query.filter(UdoProject.project_code == project_code).first()
            if udoProject:
                step = {"name": udoProject.project_name, "value": num}
                result_list.append(step)
    return ok(result_list)


@dashboard.route('/lastMonthJobTrend', methods=['GET'])
def last_month_job_trend():
    successResult = UdoRuleLog.query.with_entities(func.date_format(UdoRuleLog.start_time, "%Y-%m-%d"), func.count(1)).filter(
        and_(UdoRuleLog.check_status == 1,
             UdoRuleLog.start_time > datetime.date.today() - datetime.timedelta(days=30),
             UdoRuleLog.end_time < datetime.date.today() - datetime.timedelta(days=-1))).group_by(
        func.date_format(UdoRuleLog.start_time, "%Y-%m-%d")).all()

    failResult = UdoRuleLog.query.with_entities(func.date_format(UdoRuleLog.start_time, "%Y-%m-%d"),
                                                func.count(1)).filter(
        and_(UdoRuleLog.status != 1,
             UdoRuleLog.start_time > datetime.date.today() - datetime.timedelta(days=30),
             UdoRuleLog.end_time < datetime.date.today() - datetime.timedelta(days=-1))).group_by(
        func.date_format(UdoRuleLog.start_time, "%Y-%m-%d")).all()

    day_list = []
    days_list = []

    success_result_list = []
    fail_result_list = []

    success_number_list = []
    fail_number_list = []

    for i in range(30):
        day = datetime.date.today() - datetime.timedelta(days=i)
        day_list.append(str(day))

    for (start_time, num) in successResult:
        step = {"startTime": start_time, "num": num}
        success_result_list.append(step)

    for (start_time, num) in failResult:
        step = {"startTime": start_time, "num": num}
        fail_result_list.append(step)

    for day in day_list:
        if str(success_result_list).find(str(day)) == -1:
            step = {"startTime": day, "num": 0}
            success_result_list.append(step)

    for day in day_list:
        if str(fail_result_list).find(str(day)) == -1:
            step = {"startTime": day, "num": 0}
            fail_result_list.append(step)

    success_result_list.sort(key=lambda x: datetime.datetime.strptime(x['startTime'], "%Y-%m-%d").timestamp(), reverse=False)
    fail_result_list.sort(key=lambda x: datetime.datetime.strptime(x['startTime'], "%Y-%m-%d").timestamp(), reverse=False)

    for result in success_result_list:
        success_number_list.append(result['num'])
        days_list.append(result['startTime'])

    for result in fail_result_list:
        fail_number_list.append(result['num'])

    result_list = {"daysList": days_list, "successNumberList": success_number_list, "failNumberList": fail_number_list}
    return ok(result_list)