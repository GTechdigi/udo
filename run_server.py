# coding: utf-8
from udo import create_app, redis
import os
from udo.__version__ import __version__
from log import logger
from udo.views.auth import auth
from udo.views.project_user import projectUser
from udo.views.user import user
from udo.views.datasource import datasource
from udo.views.dashboard import dashboard
from udo.views.rule import rule
from udo.views.run_rule import runRule
from udo.views.connect import connect
from flask import request
from udo.JsonResult import failed
from udo.common.UdoErrors import UdoErrors
from udo.views.jobManager import job
from udo.views.project import project
from udo.views.metadata import metadata
from flask_cors import CORS


def main():
    main_pid = os.getpid()
    logger.info("UDO version: %s", __version__)
    logger.info("Main pid: %s", main_pid)
    app = create_app()
    CORS(app, supports_credentials=True)
    app.register_blueprint(auth)
    app.register_blueprint(user)
    app.register_blueprint(connect)
    app.register_blueprint(datasource)
    app.register_blueprint(rule)
    app.register_blueprint(runRule)
    app.register_blueprint(project)
    app.register_blueprint(job)
    app.register_blueprint(metadata)
    app.register_blueprint(dashboard)
    app.register_blueprint(projectUser)
    app.run(host=app.config['UDO_BIND'], port=app.config['UDO_PORT'], debug=app.config['DEBUG'], use_reloader=app.config['USE_RELOADER'])


@metadata.before_request
@job.before_request
@runRule.before_request
@rule.before_request
@connect.before_request
@datasource.before_request
@user.before_request
def check_login():
    try:
        if 'UDO-Token' not in request.headers.keys() and not redis.get('udo:auth:' + request.headers['UDO-Token']):
            return failed(UdoErrors.NO_LOGIN)
    except Exception as e:
        return failed(UdoErrors.NO_LOGIN)


if __name__ == '__main__':
    main()

