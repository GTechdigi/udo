from udo import db
from udo.utils.BaseModel import BaseModel


class UdoProject(BaseModel, db.Model):
    __tablename__ = 'udo_project'
    id = db.Column(db.Integer, primary_key=True)
    project_code = db.Column(db.String(60), index=True, unique=True)
    project_name = db.Column(db.String(60), index=True)
    project_description = db.Column(db.String(60), index=True)
    create_user = db.Column(db.String(60), index=True)
    create_time = db.Column(db.DATETIME, index=True)
    update_user = db.Column(db.String(60), index=True)
    update_time = db.Column(db.DATETIME, index=True)
    is_delete = db.Column(db.String(60), index=True)
    we_work_robot = db.Column(db.String(60))
