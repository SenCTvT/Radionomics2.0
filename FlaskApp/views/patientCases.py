from flask import Blueprint, render_template, redirect, url_for, request, jsonify, abort, Response, session
from FlaskApp.models.auth import Auth
from FlaskApp.models.patientCases import PatientCases
from FlaskApp.controller.upload import *
import flask
import copy
import time
import os
from FlaskApp.utils import login_required

case_bp = Blueprint('patient_cases',__name__)

#the view for the upload interface
#the backend for uploading files is provided in the api
@case_bp.route("/upload", methods = ['GET'])
@login_required
def upload():
    return render_template('dashboard.html')

#this page will show all the cases that belongs to the logged in user
@case_bp.route('/')
@login_required
def getAllCases():
    # get all the cases from the data base
    cases = PatientCases.find(session['username'])
    return render_template('case-view.html', result={ 'status': 'success', 'cases': cases })

#the page to view all the series in a case
#return 403 if the logged in user is not authorized to access the image
@case_bp.route('/<case_id>/images/', methods=['GET'])
@case_bp.route('/<case_id>/', methods=['GET'])
@login_required
def getCase(case_id):
    # get the case from db
    case = PatientCases.findCase(case_id)
    if case == None:
        abort(404)
    elif PatientCases.userHasAuthentication(case_id, session['username']):
        result = { 'status': 'success', 'case': case }
    else:
        result = { 'status': 'error', 'msg': 'You do not have sufficient authentication to access the file' }
    return render_template('series-view.html', result=result)


#the page to view all the images in a series
#return 403 if the logged in user is not authorized to access the image
@case_bp.route('/<case_id>/images/<int:index_1>/', methods=['GET'])
@case_bp.route('/<case_id>/<int:index_1>/', methods=['GET'])
@login_required
def getSeriesImages(case_id,index_1):
    # get the case from db
    series = PatientCases.findSeries(case_id, index_1)
    if series == None:
        abort(404)
    elif PatientCases.userHasAuthentication(case_id, session['username']):
        result = { 'status': 'success', 'series': series, 'index_1': index_1, 'index_2': 0 }
    else:
        result = { 'status': 'error', 'msg': 'You do not have sufficient authentication to access the file' }
    return render_template('image-view.html', result=result)

@case_bp.route('/<case_id>/images/<int:index_1>/<int:index_2>', methods=['GET'])
@case_bp.route('/<case_id>/<int:index_1>/<int:index_2>', methods=['GET'])
@login_required
def getImage(case_id,index_1,index_2):
    # get the case from db
    series = PatientCases.findSeries(case_id, index_1)
    if series == None:
        abort(404)
    elif PatientCases.userHasAuthentication(case_id, session['username']):
        result = { 'status': 'success', 'series': series, 'index_1': index_1 , 'index_2': index_2}
    else:
        result = { 'status': 'error', 'msg': 'You do not have sufficient authentication to access the file' }
    return render_template('image-view.html', result=result)

#the view for analysing the image
#Author: Debdyut
@case_bp.route("/analyse")
@login_required
def analyse():
    return render_template('image-view.html')
