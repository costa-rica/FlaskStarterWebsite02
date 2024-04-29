from flask import current_app, url_for
from flask_login import current_user
import json
from flask_mail import Message
from app_package import mail
import os
import shutil
import logging
from logging.handlers import RotatingFileHandler
import pandas as pd
from datetime import datetime
import csv
from app_package._common.utilities import custom_logger

logger_bp_users = custom_logger('bp_users.log')


def send_reset_email(user):
    token = user.get_reset_token()
    logger_bp_users.info(f"current_app.config.get(MAIL_USERNAME): {current_app.config.get('MAIL_USERNAME')}")
    msg = Message('Password Reset Request',
                  sender=current_app.config.get('MAIL_USERNAME'),
                  recipients=[user.email])

    long_f_string = (
        "To reset your password, visit the following link:" +
        f"\n {url_for('bp_users.reset_password', token=token, _external=True)} " +
        "\n\n" +
        "If you did not make this request, simply ignore this email and no changes will be made."
    )
    msg.body =long_f_string

    mail.send(msg)


def send_confirm_email(email):
    if os.environ.get('FSW_CONFIG_TYPE') == 'prod':
        logger_bp_users.info(f"-- sending email to {email} --")
        msg = Message('Welcome to Flask Starter Website',
            sender=current_app.config.get('MAIL_USERNAME'),
            recipients=[email])
        msg.body = 'You have succesfully signed up.'
        mail.send(msg)
        logger_bp_users.info(f"-- email sent --")
    else :
        logger_bp_users.info(f"-- Non prod mode, no email sent --")


