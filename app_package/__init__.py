from flask import Flask
from ._common.config import config
import os
from pytz import timezone
from datetime import datetime
from fsw_models import Base, engine
from ._common.utilities import login_manager, custom_logger_init, teardown_appcontext
from flask_mail import Mail
import secure


if not os.path.exists(os.path.join(os.environ.get('WEB_ROOT'),'logs')):
    os.makedirs(os.path.join(os.environ.get('WEB_ROOT'), 'logs'))


logger_init = custom_logger_init()

logger_init.info(f'--- Starting Flask Starter Website 01 ---')
TEMPORARILY_DOWN = "ACTIVE" if os.environ.get('TEMPORARILY_DOWN') == "1" else "inactive"
logger_init.info(f"- TEMPORARILY_DOWN: {TEMPORARILY_DOWN}")
logger_init.info(f"- FSW_CONFIG_TYPE: {os.environ.get('FSW_CONFIG_TYPE')}")


if os.environ.get('FSW_CONFIG_TYPE')=='workstation':
    logger_init.info(f"- ! This should not print if not local ! -")
    logger_init.info(f"- MYSQL_DB_URI: {config.MYSQL_DB_URI}")
    logger_init.info(f"- ! This should not print if not local ! -")


mail = Mail()
secure_headers = secure.Secure()

def create_app(config_for_flask = config):
    app = Flask(__name__)
    app.teardown_appcontext(teardown_appcontext)
    app.config.from_object(config_for_flask)
    login_manager.init_app(app)
    mail.init_app(app)

    ############################################################################
    # database
    create_folder(config_for_flask.DATABASE_ROOT)
    create_folder(config_for_flask.DIR_DB_UPLOAD)
    # create folders for PROJECT_RESOURCES
    create_folder(config_for_flask.PROJECT_RESOURCES_ROOT)
    ## website folders
    create_folder(config_for_flask.DIR_ASSETS)
    create_folder(config_for_flask.DIR_ASSETS_IMAGES)
    create_folder(config_for_flask.DIR_ASSETS_FAVICONS)
    ## blog folders
    create_folder(config_for_flask.DIR_BLOG)
    create_folder(config_for_flask.DIR_BLOG_POSTS)
    ## logs
    create_folder(config_for_flask.DIR_LOGS)
    ## media - all other videos and images
    create_folder(config_for_flask.DIR_MEDIA)
    ############################################################################
    
    # If MySQL ... here is the info
    logger_init.info(f"- MYSQL_USER: {config_for_flask.MYSQL_USER}")
    logger_init.info(f"- MYSQL_DATABASE_NAME: {config_for_flask.MYSQL_DATABASE_NAME}")

    ## If SQLite ... create db here
    if os.path.exists(os.path.join(config_for_flask.DATABASE_ROOT,os.environ.get('DB_NAME'))):
        logger_init.info(f"db already exists: {os.path.join(config_for_flask.DATABASE_ROOT,os.environ.get('DB_NAME'))}")
    else:
        # Base.metadata.create_all(dict_engine['engine_users'])
        Base.metadata.create_all(engine)
        logger_init.info(f"NEW db created: {os.path.join(config_for_flask.DATABASE_ROOT,os.environ.get('DB_NAME'))}")

    from app_package.bp_main.routes import bp_main
    from app_package.bp_users.routes import bp_users

    app.register_blueprint(bp_main)
    app.register_blueprint(bp_users)


    return app

def create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        logger_init.info(f"created: {folder_path}")