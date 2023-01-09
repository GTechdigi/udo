# coding: utf-8
from flask import Blueprint, current_app, request
from ldap3 import Server, Connection, ALL, SUBTREE, ALL_ATTRIBUTES
from udo import db, redis, CustomJSONEncoder
from udo.models.User import User
import uuid
import json
import hashlib

from udo.JsonResult import ok, failed
from udo.common.UdoErrors import UdoErrors

auth = Blueprint('auth', __name__, url_prefix='/auth')


@auth.route('/loginByLdap', methods=['GET'])
def loginByLdap():
    server = Server(current_app.config['LDAP_HOST'], port=current_app.config['LDAP_PORT'], get_info=ALL)
    conn = Connection(server, user=current_app.config['LDAP_USER'], password=current_app.config['LDAP_PASSWORD'],
                      check_names=True, lazy=False, auto_bind=True)
    conn.open()
    conn.bind()
    username = request.args.get('username')
    # username = request.json['username']
    res = conn.search(
        search_base=current_app.config['LDAP_BASE'],
        search_filter='(sAMAccountName={})'.format(username),
        search_scope=SUBTREE,
        attributes=ALL_ATTRIBUTES,
        paged_size=5
    )

    if res:
        entry = conn.response[0]
        # dn = entry['dn']
        attr_dict = entry['attributes']
        # check password by userPrincipalName
        try:
            password = request.args.get('password')
            # password = request.json['password']
            conn2 = Connection(server, user=attr_dict['userPrincipalName'], password=password,
                               check_names=True,
                               lazy=False, raise_exceptions=False)
            conn2.bind()
            if conn2.result["description"] == "success":
                user = User.query.filter_by(username=attr_dict["sAMAccountName"]).first()
                need_add = False
                if not user:
                    need_add = True
                    user = User()
                user.username = attr_dict["sAMAccountName"]
                user.first_name = attr_dict["sn"]
                user.last_name = attr_dict["givenName"]
                user.email = attr_dict["userPrincipalName"]
                if need_add:
                    db.session.add(user)
                token = uuid.uuid1()
                redis.set('udo:auth:' + str(token), json.dumps(user.to_json(), cls=CustomJSONEncoder), 7200)
                db.session.commit()
            else:
                return failed(UdoErrors.LOGIN_FAILED)
        except Exception as e:
            current_app.logger.error(e)
            return failed(UdoErrors.LOGIN_FAILED)
    else:
        return failed(UdoErrors.LOGIN_FAILED)
    return ok({'name': attr_dict["sAMAccountName"], 'token': token,
               'avatar': 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif'})


@auth.route('/login', methods=['GET'])
def login():
    username = request.args.get('username')
    password = request.args.get('password')
    user = User.query.filter_by(username=username, password=hashlib.md5(password.encode()).hexdigest()).first()
    if not user:
        return failed(UdoErrors.LOGIN_FAILED)
    token = uuid.uuid1()
    to_json = user.to_json()
    to_json['password'] = None
    redis.set('udo:auth:' + str(token), json.dumps(to_json, cls=CustomJSONEncoder), 7200)
    return ok({'name': username, 'token': token,
               'avatar': 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif'})



@auth.route('/logout', methods=['POST'])
def logout():
    if request.headers['UDO-Token']:
        redis.delete('udo:auth:' + request.headers['UDO-Token'])
    return ok(None)
