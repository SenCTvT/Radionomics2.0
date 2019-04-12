import os
from flask import Flask, Blueprint
from flask_cors import CORS
from jinja2 import Environment
from flask_session import Session
from werkzeug.utils import secure_filename
app = Flask(__name__)

#Blueprints
from views.api.test import test_bp_api
from views.api.auth import auth_bp_api
from views.api.patientCases import case_bp_api
from views.auth import auth_bp
from views.patientCases import case_bp
from views.profile import profile_bp
from views.api.utility import utility_bp_api

app.register_blueprint(test_bp_api, url_prefix = '/api/test')
app.register_blueprint(auth_bp_api, url_prefix = '/api/auth')
app.register_blueprint(case_bp_api, url_prefix = '/api/patient-cases')
app.register_blueprint(utility_bp_api, url_prefix = '/api/utility')
app.register_blueprint(case_bp,     url_prefix = '/patient-cases')
app.register_blueprint(auth_bp)
app.register_blueprint(profile_bp)

#upload configurations
UPLOAD_FOLDER = '/var/www/temp_uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_PATH'] = 1024000000

#session
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

#Cross-Origin-Requests
CORS(app)

if __name__ == '__main__':
    app.run(debug=True)
