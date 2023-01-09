from udo import db
from udo.utils.BaseModel import BaseModel


class UdoRule(BaseModel, db.Model):
    __tablename__ = 'udo_rule'
    id = db.Column(db.Integer, primary_key=True)
    project_code = db.Column(db.String(60), index=True)
    rule_code = db.Column(db.String(60), index=True)
    rule_name = db.Column(db.String(60), index=True)
    rule_description = db.Column(db.String(60), index=True)
    rule_type = db.Column(db.String(60), index=True, unique=True)
    check_db_code = db.Column(db.String(60), index=True, unique=True)
    check_db_name = db.Column(db.String(60), index=True, unique=True)
    check_table_code = db.Column(db.String(60), index=True, unique=True)
    check_table_name = db.Column(db.String(60), index=True, unique=True)
    contrast_db_code = db.Column(db.String(60), index=True, unique=True)
    contrast_db_name = db.Column(db.String(60), index=True, unique=True)
    contrast_table_code = db.Column(db.String(60), index=True, unique=True)
    contrast_table_name = db.Column(db.String(60), index=True, unique=True)
    execution_cycle = db.Column(db.String(60), index=True, unique=True)
    next_execution_time = db.Column(db.String(60), index=True, unique=True)
    last_execution_time = db.Column(db.String(60), index=True, unique=True)
    last_execution_status = db.Column(db.String(60), index=True, unique=True)
    create_user = db.Column(db.String(60), index=True, unique=True)
    create_time = db.Column(db.DATETIME, index=True, unique=True)
    update_user = db.Column(db.String(60), index=True, unique=True)
    update_time = db.Column(db.DATETIME, index=True, unique=True)
    check_source_type = db.Column(db.String(60), index=True, unique=True)
    contrast_source_type = db.Column(db.String(60), index=True, unique=True)
    check_table_sql = db.Column(db.Text)
    contrast_table_sql = db.Column(db.Text)
    alert_user = db.Column(db.Text)

    def __repr__(self):
        return self.id


class UdoRuleInfo(BaseModel, db.Model):
    __tablename__ = 'udo_rule_info'
    id = db.Column(db.Integer, primary_key=True)
    rule_code = db.Column(db.String(60), index=True)
    col = db.Column(db.String(60), index=True)
    operator = db.Column(db.String(60), index=True, unique=True)
    expected_value = db.Column(db.String(60), index=True, unique=True)
    operator_type = db.Column(db.String(60), index=True, unique=True)
    role_information = db.Column(db.String(60), index=True, unique=True)
    aggregate_type = db.Column(db.String(20))
    expression = db.Column(db.Integer())


class UdoRuleLog(BaseModel, db.Model):
    __tablename__ = 'udo_rule_log'
    id = db.Column(db.Integer, primary_key=True)
    project_code = db.Column(db.String(60), index=True, default="")
    project_name = db.Column(db.String(60), index=True, default="")
    rule_code = db.Column(db.String(60), index=True)
    rule_name = db.Column(db.String(60), index=True)
    rule_description = db.Column(db.String(60), index=True)
    rule_type = db.Column(db.String(60), index=True, unique=True)
    start_time = db.Column(db.TIMESTAMP)
    end_time = db.Column(db.TIMESTAMP)
    status = db.Column(db.Integer)
    check_status = db.Column(db.Integer)
    content = db.Column(db.TEXT)

