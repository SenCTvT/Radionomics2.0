from flask import Blueprint, render_template, redirect, url_for, request, jsonify, abort, Response, session
from FlaskApp.models.auth import Auth
from FlaskApp.controller.Spectroscopy import spectDisc

utility_bp = utility_bp_api = Blueprint('utility_api', __name__)

@utility_bp.route('/get-spectroscopy')
def spectroscopy():
    result = {
        'error' : {}
        }
    #if username is in session then the call is web call, so use that username
    if 'username' in session and len(session['username']) > 0:
        username = session['username']
    else:
        if 'key' not in request.args or len(request.args['key']) == 0:
            result['error']['error'] = True
            result['error']['error_message'] = "key not specified"
            return jsonify(result)

        auth_result = Auth.checkKeyValidity(request.args['key'])

        if not auth_result['valid']:
            result['error']['error'] = True
            result['error']['error_message'] = "key not valid"
            return jsonify(result)

    #Authentication is done

    if 'pixel' not in request.args:
        result['error']['error'] = True
        result['error']['error_message'] = "pixel not provided"
        return jsonify(result)
    elif not request.args['pixel'].isdigit() or int(request.args['pixel']) > 255 or int(request.args['pixel']) < 0:
        result['error']['error'] = True
        result['error']['error_message'] = "invalid pixel"
        return jsonify(result)
    elif int(request.args['pixel']) < 85:
        result['error']['error'] = True
        result['error']['error_message'] = "spectroscopy not available"
        return jsonify(result)

    result['error']['error'] = False

    result['x']=(0,0.5,0.8,1.3,1.4,1.5,1.6,1.8,2,2.4,2.6,2.8,3,3.2,3.4,3.6,3.7,3.9,4,4.4)
    result['y']=spectDisc[int(request.args['pixel'])]
    result['labels'] =('','','LIP','','LAC','','','','NAA','GLM','','','CR','','CHO','','MI','','CR2','')

    return jsonify(result)


@utility_bp.route('/get-disease-names')
def getDiseaseNames():
    return jsonify(['normal','csf','edma','MS','cyst','glioma','glioblastoma','lymphoma','metastesis'])
