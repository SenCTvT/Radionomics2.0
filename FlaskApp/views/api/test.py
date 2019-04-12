from flask import Blueprint, session, jsonify
from FlaskApp.models.auth import Auth
from FlaskApp.models.patientCases import PatientCases, DicomImage, DicomSeries
from FlaskApp.controller.MLdataset import MLdataset
test_bp_api = test_bp = Blueprint('test_api',__name__)

@test_bp.route('/hello')
def home1():
    return "done 1234"

@test_bp.route("/test-key/<key>")
def testKey(key):
    return str(Auth.checkKeyValidity(key))

@test_bp.route("/save-patient-case")
def savePatient():
    patient_name = "Ritwik"
    patient_age = 21
    username = "ritwik"
    files = [
            DicomSeries('152265', 'T2 MRI', [
                DicomImage('IMG5465.dcm', 'dksdfisdfjijskdk'),
                DicomImage('IMG4465.dcm', 'dksdfisdfjijskds')
            ]),
            DicomSeries('152265', 'T1 MRI', [
                DicomImage('IMG5467.dcm', 'dksdfissfjijskdk'),
                DicomImage('IMG4468.dcm', 'dksdfisdfjijsdds')
            ])
    ]

    patient_cases = PatientCases(username, patient_name, patient_age, files)

    caseid = patient_cases.save()

    return "done"

@test_bp.route("/login/<username>")
def login(username):
    session['username'] = username
    return ""

@test_bp.route("/logout")
def logout():
    session.pop('username')
    return ""


@test_bp.route("/ml")
def ml():
    return jsonify(MLdataset.getDataSet())
