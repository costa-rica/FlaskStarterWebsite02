
from flask import Blueprint
from flask import render_template, url_for, redirect, flash, request, \
    abort, session, Response, current_app, send_from_directory, make_response, \
    send_file, jsonify, g
import bcrypt
from flask_login import login_required, login_user, logout_user, current_user
# import logging
# from logging.handlers import RotatingFileHandler
from app_package._common.utilities import custom_logger
import os
import json
# from ws_models import sess, engine, text, Users
from fsw_models import engine, DatabaseSession, text, Users
# from app_package.bp_users.utils import  create_shortname_list, api_url
from app_package.bp_users.utils import send_reset_email, send_confirm_email
import datetime
import requests
import zipfile
from app_package._common.utilities import custom_logger, wrap_up_session


logger_bp_users = custom_logger('bp_users.log')
salt = bcrypt.gensalt()
bp_users = Blueprint('bp_users', __name__)

@bp_users.before_request
def before_request():
    logger_bp_users.info("-- def before_request() --")
    # Assign a new session to a global `g` object, accessible during the whole request
    g.db_session = DatabaseSession()
    
    # Use getattr to safely access g.referrer, defaulting to None if it's not set
    if getattr(g, 'referrer', None) is None:
        if request.referrer:
            g.referrer = request.referrer
        else:
            g.referrer = "No referrer"
    
    logger_bp_users.info("-- def before_request() END --")


@bp_users.route('/login', methods = ['GET', 'POST'])
def login():
    logger_bp_users.info('- in login -')
    logger_bp_users.info(f'- g.referrer: {g.referrer} -')
    db_session = g.db_session

    if current_user.is_authenticated:
        return redirect(url_for('bp_main.home'))
    
    logger_bp_users.info(f'- in login route')

    page_name = 'Login'
    if request.method == 'POST':
        formDict = request.form.to_dict()
        logger_bp_users.info(f"formDict: {formDict}")
        email = formDict.get('email')

        user = db_session.query(Users).filter_by(email=email).first()
        password = formDict.get('password')

        if user:
            if password:
                # if bcrypt.checkpw(password.encode(), user.password.encode()):
                if bcrypt.checkpw(password.encode(), user.password):
                    login_user(user)
                    return redirect(url_for('bp_main.home'))
                else:
                    flash('Password or email incorrectly entered', 'warning')
            else:
                flash('Must enter password', 'warning')
        else:
            flash('No user by that name', 'warning')


    return render_template('users/login.html', page_name = page_name)

@bp_users.route('/register', methods = ['GET', 'POST'])
def register():
    logger_bp_users.info('- in register -')
    logger_bp_users.info(f'- g.referrer: {g.referrer} -')
    db_session = g.db_session
    if current_user.is_authenticated:
        return redirect(url_for('bp_main.home'))
    page_name = 'Register'
    if request.method == 'POST':
        formDict = request.form.to_dict()
        new_email = formDict.get('email')

        check_email = db_session.query(Users).filter_by(email = new_email).all()

        logger_bp_users.info(f"check_email: {check_email}")

        if len(check_email)==1:
            flash(f'The email you entered already exists you can sign in or try another email.', 'warning')
            return redirect(url_for('bp_users.register'))

        hash_pw = bcrypt.hashpw(formDict.get('password').encode(), salt)
        new_user = Users(email = new_email, password = hash_pw)
        db_session.add(new_user)

        # Send email confirming succesfull registration
        try:
            if new_email not in current_app.config.get('LIST_NO_CONFIRMASTION_EMAILS'):
                send_confirm_email(new_email)
        except:
            flash(f'Problem with email: {new_email}', 'warning')
            return redirect(url_for('bp_users.login'))

        #log user in
        logger_bp_users.info('--- new_user ---')
        logger_bp_users.info(new_user)
        login_user(new_user)
        flash(f'Succesfully registered: {new_email}', 'info')
        return redirect(url_for('bp_main.home'))

    return render_template('users/register.html', page_name = page_name)

@bp_users.route('/logout')
def logout():
    logger_bp_users.info(f'- g.referrer: {g.referrer} -')
    logout_user()
    return redirect(url_for('bp_main.home'))

@bp_users.route('/request_reset_password', methods = ["GET", "POST"])
def request_reset_password():

    logger_bp_users.info('- in register -')
    db_session = DatabaseSession()

    page_name = 'Request Password Change'
    if current_user.is_authenticated:
        return redirect(url_for('bp_main.home'))

    if request.method == 'POST':
        formDict = request.form.to_dict()
        email = formDict.get('email')
        user = db_session.query(Users).filter_by(email=email).first()
        
        if user:
            send_reset_email(user)
        
        wrap_up_session(db_session, logger_bp_users)

        return redirect(url_for('bp_users.request_reset_password'))
    return render_template('users/reset_request.html', page_name = page_name)

@bp_users.route('/reset_password', methods = ["GET", "POST"])
def reset_password():
    page_name = "Reset Password"
    logger_bp_users.info('- in reset_password with token -')
    db_session = DatabaseSession()

    token = request.args.get('token')
    user = Users.verify_reset_token(token)
    logger_bp_users.info(f'user:: {user}')
    
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('bp_users.reset_password'))
    if request.method == 'POST':
        formDict = request.form.to_dict()
        new_user_obj = db_session.get(Users,user.id)
        hash_pw = bcrypt.hashpw(formDict.get('password_text').encode(), salt)
        new_user_obj.password = hash_pw
        wrap_up_session(db_session, logger_bp_users)


        return redirect(url_for('bp_users.login'))
    return render_template('users/reset_request.html', page_name = page_name)
