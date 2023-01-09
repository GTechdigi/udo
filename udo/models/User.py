from udo import db
from udo.utils.BaseModel import BaseModel


class User(BaseModel, db.Model):
    __tablename__ = 'udo_user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(60), index=True)
    last_name = db.Column(db.String(60), index=True)
    username = db.Column(db.String(60), index=True, unique=True)
    phone = db.Column(db.String(15), index=True, unique=True)
    email = db.Column(db.String(60), index=True, unique=True)
    create_time = db.Column(db.DATETIME, index=True, unique=True)
    update_time = db.Column(db.DATETIME, index=True, unique=True)
    password = db.Column(db.String(200))

    def __repr__(self):
        return self.id

