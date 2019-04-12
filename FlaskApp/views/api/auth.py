from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from FlaskApp.models.auth import Auth
from FlaskApp.models.user import User
from validate_email import validate_email
import hashlib


auth_bp_api = auth_bp = Blueprint('auth_api',__name__)

#get api access key
@auth_bp.route('/get-key',methods=['POST'])
def getKey():
    response = {}
    if 'username' not in request.form or 'password' not in request.form:
        response['error'] = True
        return jsonify(response)

    username = request.form['username']
    password = hashlib.sha512(request.form['password']).hexdigest()

    #checking for authentication
    auth_resp = Auth.authorize(username, password)

    if auth_resp['success']:
        response['error'] = False
        response['key'] = auth_resp['key']
    else:
        response['error'] = True

    return jsonify(response)


#new user
@auth_bp.route('/new',methods=['POST'])
def newUser():

    #check if all compulsory parameters are present
    if 'name' not in request.form or'username' not in request.form or 'password' not in request.form or 'email' not in request.form or 'doctor_reg_id' not in request.form:
        response = {}
        response['success'] = False
        response['error_msg'] = "All mandetory parameters are not present"
        return jsonify(response)

    #get the request parameters
    name = request.form['name']
    username = request.form['username']
    password = request.form['password']
    if 'phone' in request.form:
        phone = request.form['phone']
    else:
        phone = None
    email = request.form['email']
    doctor_id = request.form['doctor_reg_id']

    #check if all compulsory parameters are non-empty
    if name == "" or username == "" or password == "" or email == "" or doctor_id == "":
        response = {}
        response['success'] = False
        response['error_msg'] = "All mandetory parameters are not present"
        return jsonify(response)

    #check if username already exists
    if User.usernameExists(username):
        response = {}
        response['success'] = False
        response['error_msg'] = "Username already exists"
        return jsonify(response)

    #check if doctor id already exists
    if User.doctorIdExists(doctor_id):
        response = {}
        response['success'] = False
        response['error_msg'] = "Doctor id already exists"
        return jsonify(response)

    #check if email already exists
    if not validate_email(email) or User.emailExists(email):
        response = {}
        response['success'] = False
        response['error_msg'] = "Email already exists or is of invalid format"
        return jsonify(response)

    #check if password if of propper format
    if len(password) < 6:
        response = {}
        response['success'] = False
        response['error_msg'] = "Password length should be atleast 6."
        return jsonify(response)

    password = hashlib.sha512(password).hexdigest()

    user = User(name, username, email, phone, password, doctor_id)
    user.save()

    #send success message
    response = {}
    response['success'] = True
    return jsonify(response)


@auth_bp.route('/check-username',methods=['GET'])
def checkUsername():
    result = {}
    if 'username' not in request.args:
        result['valid'] = False
        return jsonify(result)
    elif User.usernameExists(request.args['username']):
        result['valid'] = False
        return jsonify(result)
    else:
        result['valid'] = True
        return jsonify(result)


@auth_bp.route('/check-doctor-id',methods=['GET'])
def checkDoctorId():
    result = {}
    if 'did' not in request.args:
        result['valid'] = False
        return jsonify(result)
    elif User.doctorIdExists(request.args['did']):
        result['valid'] = False
        return jsonify(result)
    else:
        result['valid'] = True
        return jsonify(result)


@auth_bp.route('/check-email',methods=['GET'])
def checkEmail():
    result = {}
    if 'email' not in request.args:
        result['valid'] = False
        return jsonify(result)
    elif not validate_email(request.args['email']) or User.emailExists(request.args['email']):
        result['valid'] = False
        return jsonify(result)
    else:
        result['valid'] = True
        return jsonify(result)


@auth_bp.route('/change-password',methods=['POST'])
def changePassword():
    response = {}
    if 'key' not in request.form or 'old-password' not in request.form or 'new-password' not in request.form :
        response['error'] = True
        response['error_msg'] = 'All fields are mandetory'
        return jsonify(response)

    key = request.form['key']
    old_password = request.form['old-password']
    new_password = request.form['new-password']

    auth_resp = Auth.checkKeyValidity(key)

    if not auth_resp['valid'] :
        response['error'] = True
        response['error_msg'] = 'Invalid API key'
        return jsonify(response)

    username = auth_resp['username']

    if old_password == "" or new_password == "":
        response['error'] = True
        response['error_msg'] = 'Empty parameters'
        return jsonify(response)

    if len(new_password) < 6:
        response['error'] = True
        response['error_msg'] = 'Length of password must be atleast 6'
        return jsonify(response)

    old_password = hashlib.sha512(old_password).hexdigest()
    new_password = hashlib.sha512(new_password).hexdigest()

    if not User.passwordValid(username, old_password):
        response['error'] = True
        response['error_msg'] = 'Old password not valid'
        return jsonify(response)

    User.changePassword(username, new_password)
    response['error'] = False
    return jsonify(response)
