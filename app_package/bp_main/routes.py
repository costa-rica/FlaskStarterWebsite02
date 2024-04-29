from flask import Blueprint
from flask import render_template, current_app, send_from_directory, g, request
import os
from app_package._common.utilities import custom_logger
import datetime
from flask_login import login_required, login_user, logout_user, current_user


logger_bp_main = custom_logger('bp_main.log')
bp_main = Blueprint('bp_main', __name__)

@bp_main.before_request
def before_request():
    logger_bp_main.info("-- def before_request() --")
    # Assign a new session to a global `g` object, accessible during the whole request
    # g.db_session = DatabaseSession()
    # Use getattr to safely access g.referrer, defaulting to None if it's not set
    if getattr(g, 'referrer', None) is None:
        if request.referrer:
            g.referrer = request.referrer
        else:
            g.referrer = "No referrer"
    
    logger_bp_main.info("-- def before_request() END --")

@bp_main.route("/", methods=["GET","POST"])
def home():
    logger_bp_main.info(f"-- in home page route --")
    logger_bp_main.info(f'- g.referrer: {g.referrer} -')
    # Get today's date
    today = datetime.date.today()

    # Format the date as a string with the full month name, date, and year
    formatted_date = today.strftime("%B %d, %Y")

    return render_template('main/home.html', formatted_date = formatted_date)

@bp_main.route("/page2", methods=["GET","POST"])
@login_required
def page2():
    logger_bp_main.info(f"-- in page2 route --")
    logger_bp_main.info(f'- g.referrer: {g.referrer} -')
    # Get today's date
    today = datetime.date.today()

    # Format the date as a string with the full month name, date, and year
    formatted_date = today.strftime("%B %d, %Y")

    return render_template('main/page2.html', formatted_date = formatted_date)

# Website Assets static data
@bp_main.route('/website_assets_favicon/<filename>')
def website_assets_favicon(filename):
    logger_bp_main.info("-- in website_assets_favicon -")
    file_to_server = os.path.join(current_app.config.get('DIR_ASSETS_FAVICONS'), filename)
    logger_bp_main.info(f"file_to_server: {file_to_server}")
    # print(f"Path to image file: {current_app.config.get('DIR_WEBSITE_UTILITY_IMAGES')}")
    # print(f"image filename: {filename}")
    return send_from_directory(current_app.config.get('DIR_ASSETS_FAVICONS'), filename)
