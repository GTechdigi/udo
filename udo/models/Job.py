from udo import db
from udo.utils.BaseModel import BaseModel


class UdoJobInfo(BaseModel, db.Model):
    __tablename__ = 'udo_job_info'
    id = db.Column(db.Integer, primary_key=True)
    project_code = db.Column(db.String(60), index=True, default="")
    job_id = db.Column(db.String(60), index=True)
    job_name = db.Column(db.String(60), index=True)
    rule_code = db.Column(db.String(60), index=True)
    trigger = db.Column(db.String(60), index=True)
    run_date = db.Column(db.DATETIME, index=True, unique=True)
    start_date = db.Column(db.DATETIME, index=True, unique=True)
    end_date = db.Column(db.DATETIME, index=True, unique=True)
    year = db.Column(db.Integer, index=True, unique=True)
    month = db.Column(db.Integer, index=True, unique=True)
    week = db.Column(db.Integer, index=True, unique=True)
    day = db.Column(db.Integer, index=True, unique=True)
    day_of_week = db.Column(db.Integer, index=True, unique=True)
    hour = db.Column(db.Integer, index=True, unique=True)
    minute = db.Column(db.Integer, index=True, unique=True)
    second = db.Column(db.Integer, index=True, unique=True)
    next_run_time = db.Column(db.DATETIME, index=True, unique=True)
    status = db.Column(db.Integer, index=True, unique=True)
    create_time = db.Column(db.DATETIME, index=True, unique=True)
    create_user = db.Column(db.String(60), index=True, unique=True)
    update_time = db.Column(db.DATETIME, index=True, unique=True)
    update_user = db.Column(db.String(60), index=True, unique=True)
    is_run = db.Column(db.Integer, index=True, unique=True, default=1)

class UdoJob(BaseModel, db.Model):
    __tablename__ = 'udo_job'
    id = db.Column(db.Integer, primary_key=True)
    next_run_time = db.Column(db.Float, index=True, unique=True)
    job_state = db.Column(db.BLOB, index=True, unique=True)
