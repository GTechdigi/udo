from flask import Flask, current_app
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from flask_redis import FlaskRedis
from flask_apscheduler import APScheduler
from log import logger
from udo.common.CustomJSONEncoder import CustomJSONEncoder
from pprint import pformat
from apscheduler.events import EVENT_ALL

db = SQLAlchemy()
redis = FlaskRedis()
mail = Mail()
scheduler = APScheduler()


def my_listener(event):
    msg = "%s: \n%s\n" % (event.code, pformat(vars(event), indent=4))
    logger.info(msg)


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )
    app.config.from_object('udo.default_settings')
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # a simple page that says hello
    @app.route('/')
    def hello():
        logger.info('Hello, Udo!')
        return 'Hello, Udo!'

    app.json_encoder = CustomJSONEncoder
    db.init_app(app)
    redis.init_app(app)
    mail.init_app(app)
    scheduler.init_app(app)
    scheduler.add_listener(my_listener, EVENT_ALL)
    scheduler.start()
    return app

