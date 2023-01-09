from flask import Blueprint, current_app, request
from udo import redis, db, default_settings
import json
from udo.JsonResult import ok, failed, ok_base_page
from udo.models.User import User
from udo.utils import Page
from udo.services import user_service
from udo.common.UdoErrors import UdoErrors
import hashlib

user = Blueprint('user', __name__, url_prefix='/user')


@user.route('/current_info')
def current_user_info():
    if request.headers['UDO-Token']:
        user_cache = redis.get('udo:auth:' + request.headers['UDO-Token'])
        if user_cache:
            result = json.loads(user_cache)
            result['roles'] = ['admin']
            result['avatar'] = 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif'
            return ok(result)


@user.route('/add', methods=['POST'])
def add_user():
    username = user_service.get_current_user(request)
    if username in default_settings.ADMIN:
        user_add = request.get_json()
        user_model = User()
        user_model.username = user_add['username']
        user_model.first_name = user_add['first_name']
        user_model.last_name = user_add['last_name']
        user_model.password = hashlib.md5(user_add['password'].encode()).hexdigest()
        user_model.email = user_add['email']
        db.session.add(user_model)
        return ok(None)
    else:
        return failed(UdoErrors.PERMISSION_FAILED)


@user.route('/<username>', methods=['GET'])
def current_user(username=None):
    user_info = User.query.filter_by(username=username).first()
    return ok(user_info)


@user.route('/list', methods=['GET'])
def query_user_list():
    page_num = int(request.args.get('page_num') or 1)
    page_size = int(request.args.get('page_size') or 10)
    user_info = User.query.order_by(User.create_time.desc())
    user_list, total = Page.page(user_info, page_num, page_size)
    return ok_base_page(user_list, total)
