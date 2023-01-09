from udo import db
from udo.utils.BaseModel import BaseModel


class OperateLog(BaseModel, db.Model):
    __tablename__ = 'udo_operate_log'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(60), index=True, unique=True)
    type = db.Column(db.String(60), index=True)
    db_code = db.Column(db.String(60), index=True)
    project_code = db.Column(db.String(60), index=True)
    rule_code = db.Column(db.String(60), index=True)
    job_code = db.Column(db.String(60), index=True)
    ip = db.Column(db.String(60), index=True)
    request_body = db.Column(db.String(60), index=True)
    output = db.Column(db.String(60), index=True)
    create_user = db.Column(db.String(60), index=True)
    create_time = db.Column(db.DATETIME, index=True)
