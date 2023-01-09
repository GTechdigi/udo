from enum import Enum, unique


@unique
class UdoErrors(Enum):
    NO_LOGIN = ('0001', '未登录')
    LOGIN_FAILED = ('0002', '用户名或密码错误')
    CONNECT_FAILED = ('0003', '连接失败')
    CREATE_FAILED = ('0004', '数据源已存在')
    NO_JOB = ('0005', '没有对应的job_id!')
    DELETE_FAILED = ('0006', '删除失败!')
    ADD_FAILED = ('0007', '用户已存在!')
    ADD_PROJECT_FAILED = ('0008', '项目已存在!')
    PERMISSION_FAILED = ('0009', '此操作您没有权限!')
    SQL_NULL_FAILED = ('0010', 'sql语句不能为空!')
    SQL_ERROR_FAILED = ('0011', 'sql语句解密出错!')


