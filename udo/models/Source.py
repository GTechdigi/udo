from udo import db
from udo.utils.BaseModel import BaseModel


class DatabaseSource(BaseModel, db.Model):
    __tablename__ = 'udo_source_database'
    id = db.Column(db.Integer, primary_key=True)
    source_type = db.Column(db.String(60), index=True)
    source_name = db.Column(db.String(60), index=True)
    host = db.Column(db.String(60), index=True, unique=True)
    db_name = db.Column(db.String(60), index=True, unique=True)
    port = db.Column(db.String(15), index=True, unique=True)
    user = db.Column(db.String(60), index=True, unique=True)
    password = db.Column(db.String(60), index=True, unique=True)
    db_code = db.Column(db.String(60), index=True, unique=True)
    create_time = db.Column(db.DATETIME)
    update_time = db.Column(db.DATETIME)

    def __repr__(self):
        return self.id


class TableSource(BaseModel, db.Model):
    __tablename__ = 'udo_source_table'
    id = db.Column(db.Integer, primary_key=True)
    source_type = db.Column(db.String(60), index=True)
    table_name = db.Column(db.String(200), index=True, unique=True)
    db_code = db.Column(db.String(60), index=True, unique=True)
    table_code = db.Column(db.String(60), index=True, unique=True)

    def __repr__(self):
        return self.id


class FieldSource(BaseModel, db.Model):
    __tablename__ = 'udo_source_field'
    id = db.Column(db.Integer, primary_key=True)
    source_type = db.Column(db.String(16), index=True)
    field_name = db.Column(db.String(255), index=True, unique=True)
    field_type = db.Column(db.String(128), index=True, unique=True)
    field_describe = db.Column(db.String(255), index=True, unique=True)
    default_value = db.Column(db.String(255), index=True, unique=True)
    is_null = db.Column(db.String(255), index=True, unique=True)
    Index_info = db.Column(db.String(255), index=True, unique=True)
    primary_key = db.Column(db.String(255), index=True, unique=True)
    db_code = db.Column(db.String(60), index=True, unique=True)
    table_code = db.Column(db.String(60), index=True, unique=True)

    def __repr__(self):
        return self.id





