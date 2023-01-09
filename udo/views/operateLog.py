import json
import datetime
from udo import db, redis
from udo.models.OperateLog import OperateLog
from flask import request


def addOperateLog(Operate):
    user_cache = redis.get('udo:auth:' + request.headers['UDO-Token'])
    result = json.loads(user_cache)
    create_user = result['username']
    new_data = OperateLog(
        url=Operate['url'],
        type=Operate['type'],
        db_code=Operate['db_code'],
        project_code=Operate['project_code'],
        rule_code=Operate['rule_code'],
        job_code=Operate['job_code'],
        ip=Operate['ip'],
        request_body=Operate['request_body'],
        output=Operate['output'],
        create_user=create_user,
        create_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    db.session.add(new_data)
