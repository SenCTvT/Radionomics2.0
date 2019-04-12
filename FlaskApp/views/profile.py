from flask import Blueprint, render_template, redirect, url_for, request, jsonify, abort, Response, session
from FlaskApp.models.auth import Auth
from FlaskApp.models.patientCases import PatientCases
from FlaskApp.controller.upload import *
import flask
import copy
import time
import os


profile_bp = Blueprint('profile',__name__)

@profile_bp.route('/')
@profile_bp.route('/home')
def home():
    return render_template('home.html')


@profile_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('profile.home'))
