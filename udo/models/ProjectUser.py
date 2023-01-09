from udo import db
from udo.utils.BaseModel import BaseModel


class UdoProjectUser(BaseModel, db.Model):
    __tablename__ = 'udo_project_user'
    id = db.Column(db.Integer, primary_key=True)
    project_code = db.Column(db.String(60), index=True, unique=True)
    username = db.Column(db.String(60), index=True)
    create_user = db.Column(db.String(60), index=True)
    create_time = db.Column(db.DATETIME, index=True)
    update_user = db.Column(db.String(60), index=True)
    update_time = db.Column(db.DATETIME, index=True)