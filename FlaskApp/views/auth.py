from flask import Blueprint, render_template, redirect, url_for, request, jsonify, session
from FlaskApp.models.auth import Auth
from FlaskApp.models.user import User
from validate_email import validate_email
import hashlib
from FlaskApp.utils import login_required
import urllib
import urllib2

auth_bp = Blueprint('auth',__name__)


@auth_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@auth_bp.route('/auth', methods=['GET','POST'])
def auth():
    resp = request.form
    if 'username' in session and len(session['username']) > 0:
        return redirect(url_for('auth.dashboard'))
    return render_template('auth.html', result=resp)


@auth_bp.route('/login', methods=['GET','POST'])
def login():
    result = {}
    if 'username' not in request.form or 'password' not in request.form:
        result['error'] = True
        return redirect(url_for('auth.auth'), 302, result)

    username = request.form['username']
    password = hashlib.sha512(request.form['password']).hexdigest()

    # checking for authentication
    auth_resp = Auth.authorize(username, password)
    session['username'] = username

    if auth_resp['success']:
        return redirect(url_for('auth.dashboard'))
    else:
        result['error'] = True
        return redirect(url_for('auth.auth'), 302, result)


@auth_bp.route("/register", methods=['GET','POST'])
def register():
    login()


@auth_bp.route("/change-password", methods=['GET','POST'])
def changePassword():
    return ""


@auth_bp.route("/try", methods=['GET','POST'])
def tryy():
    return render_template('layout.html')