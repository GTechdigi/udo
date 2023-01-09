from udo import db
from udo.utils.BaseModel import BaseModel


class Metadata(BaseModel, db.Model):
    __tablename__ = 'udo_metadata'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(60), index=True)
    code = db.Column(db.String(60), index=True)
    parent = db.Column(db.String(60), index=True, unique=True)
    value = db.Column(db.String(60), index=True, unique=True)
    sort = db.Column(db.Integer, index=True, unique=True)
    multiple = db.Column(db.Integer, index=True, unique=True)

    def __repr__(self):
        return self.id





