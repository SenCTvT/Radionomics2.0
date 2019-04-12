from flask import Blueprint, render_template, redirect, url_for, request, jsonify, abort, Response, session
from FlaskApp.models.auth import Auth
from FlaskApp.models.patientCases import PatientCases, DicomImage, DicomSeries
from FlaskApp.controller.upload import *
from FlaskApp.config.appconfig import BASE_URL, UPLOAD_DIR
from FlaskApp.controller.DicomValidatorGroup import DicomDirValidator, DicomSeriesValidator
from FlaskApp.controller.DicomDecoder import DicomDecoder
from FlaskApp.controller.Conversions import *
from FlaskApp.controller.FeatureExtract import Cluster, SingleClusterer
from FlaskApp.models.analysisResult import AnalysisResult, InfectedAreas
from FlaskApp.controller.Segment import *
import flask
import copy
import time
import os
import random


case_bp_api = case_bp = Blueprint('patient_cases_api',__name__)

@case_bp.route("/")
def getAllCases():
    result = {
        'error' : {}
        }
    #if username is in session then the call is web call, so use that username
    if 'username' in session and len(session['username']) > 0:
        username = session['username']
    else:
        if 'key' not in request.args or len(request.args['key']) == 0:
            result['error']['error'] = True
            result['error']['error_msgessage'] = "key not specified"
            return jsonify(result)

        auth_result = Auth.checkKeyValidity(request.args['key'])

        if not auth_result['valid']:
            result['error']['error'] = True
            result['error']['error_msgessage'] = "key not valid"
            return jsonify(result)

        username = auth_result['username']

    if 'page' in request.args:
        page = int(request.args['page'])
    else:
        page = None

    result['error']['error'] = False
    result['cases'] = []
    cases = PatientCases.find(username, page)
    #return str(cases)
    if cases is None:
        result['error']['error'] = True
        result['error']['error_msgessage'] = "No cases found"
        return jsonify(result)
    for case in cases:
        cs = {}
        cs['patient_name'] = case['patient_name']
        cs['patient_age'] = case['patient_age']
        cs['case_id'] = str(case["_id"])
        if 'case_name' in case:
            cs['case_name'] = case['case_name']
        if 'datetime' in case:
            cs['datetime'] = case['datetime']

        if 'ignore_images' not in request.args or request.args['ignore_images'] == 'false':
            cs['files'] = []
            i = 0
            for series in case['files']:
                s = {}
                s['series_description'] = series['series_description']
                s['series_time'] = series['series_time']
                j=0
                s['images'] = []
                for image in series['images']:
                    im = {}
                    im['url'] = BASE_URL + url_for('patient_cases_api.getImage', case_id = str(case["_id"]), index_1 = i, index_2 = j)
                    im['filename'] = image['org_filename']
                    s['images'].append(im)
                    j+=1
                cs['files'].append(s)
                i+=1
        result['cases'].append(cs)
    return jsonify(result)

#get case details
@case_bp.route('/<case_id>/')
def getCase(case_id):
    result = {
        'error' : {}
        }
    #if username is in session then the call is web call, so use that username
    if 'username' in session and len(session['username']) > 0:
        username = session['username']
    else:
        if 'key' not in request.args or len(request.args['key']) == 0:
            result['error']['error'] = True
            result['error']['error_msgessage'] = "key not specified"
            return jsonify(result)

        auth_result = Auth.checkKeyValidity(request.args['key'])

        if not auth_result['valid']:
            result['error']['error'] = True
            result['error']['error_msgessage'] = "key not valid"
            return jsonify(result)

        username = auth_result['username']

    if not PatientCases.userHasAuthentication(case_id, username):
        result['error']['error'] = True
        result['error']['error_msgessage'] = "logged in user do not have permission to acccess this case"
        return jsonify(result)

    case_result = PatientCases.findCase(case_id)

    if case_result == None:
        result['error']['error'] = True
        result['error']['error_msgessage'] = "Case id not valid"
        return jsonify(result)

    #Now that the authentication is done process the result and respond according to the api refference
    result['error']['error'] = False
    result['patient_name'] = case_result['patient_name']
    result['patient_age'] = case_result['patient_age']
    result['case_id'] = str(case_result["_id"])
    if 'case_name' in case_result:
        result['case_name'] = case_result['case_name']
    if 'datetime' in case_result:
        result['datetime'] = case_result['datetime']

    if 'ignore_images' in request.args and request.args['ignore_images'] != 'false':
        return jsonify(result)

    #take the files from the case result
    files =  case_result['files']
    result['images'] = []
    i = 0 #to keep track of index_1
    for file in files:
        series = {}
        series['series_description'] = file['series_description']
        series['series_time'] = file['series_time']
        series['images'] = []
        j = 0 #to keep track of index_2
        for image in file['images']:
            img = {}
            img['filename'] = image['org_filename']
            img['url'] = BASE_URL + url_for('patient_cases_api.getImage', case_id = case_id, index_1 = i, index_2 = j)
            j+=1
            series['images'].append(img)
        i+=1
        result['images'].append(series)

    return jsonify(result)

#Upload
@case_bp.route('/upload', methods=['POST'])
def upload():
    response = { "error"  : {} }
    #if username is in session then the call is web call, so use that username
    if 'username' in session and len(session['username']) > 0:
        username = session['username']
    else:
        if 'key' not in request.form or len(request.form['key']) == 0:
            response['error']['error'] = True
            response['error']['error_message'] = "key not specified"
            response['error']['error_type'] = "AUTH_ERROR"
            return jsonify(response)

        auth_result = Auth.checkKeyValidity(request.form['key'])

        if not auth_result['valid']:
            response['error']['error'] = True
            response['error']['error_message'] = "key not valid"
            response['error']['error_type'] = "AUTH_ERROR"
            return jsonify(response)

        username = auth_result['username']

    if 'case_name' in request.form:
        case_name = request.form['case_name']
    else:
        case_name = None

    uploaded_files = flask.request.files.getlist("files[]")
    if len(uploaded_files) == 0:
        response['error']['error'] = True
        response['error']['error_message'] = "Files not Selected"
        response['error']['error_type'] = "PARAMETER_ERROR"
        return jsonify(response)
    #print uploaded_files
    files = []
    #directory = '/var/www/temp_uploads/'
    directory = UPLOAD_DIR
    print "Uploading to directory: " + directory;
    for f in uploaded_files:
         fi = {}
         name = os.path.splitext(f.filename)[0]
         suffix = time.time()
         filename = name + str(suffix)
         filename = filename.replace('.','')
         fi['name_on_disk'] = filename
         fi['original_name'] = f.filename
         files.append(fi)
         f.save(os.path.join(directory, filename))

    result = Upload(files)

    if result.errorPresent:
        response['error'] = result.error
        return jsonify(response)
    else:
        #group the images
        dv = DicomDirValidator(result.validators)
        dicomSeries = []
        i=0
        response['images'] = []
        for series in dv.series:
            images = []
            res_images = {}
            res_images['series_time'] = series.seriesTime
            res_images['series_description'] = series.seriesDescription
            res_images['images'] = []
            for validator in series.dv:
                images.append(DicomImage(validator['org_filename'], validator['disk_filename']))
                image = {}
                image['filename'] = validator['org_filename']
                res_images['images'].append(image)
            response['images'].append(res_images)
            dicomSeries.append(DicomSeries(series.seriesTime, series.seriesDescription, images))
        case_id = PatientCases(username, case_name, dv.patientName, dv.patientAge, dicomSeries).save()
        response['case_id'] = case_id
        response['patient_name'] = dv.patientName
        if case_name != None:
            response['case_name'] = case_name
        response['patient_age'] = dv.patientAge
        response['error']['error'] = False
        i = 0
        for series in response['images']:
            j=0
            for image in series['images']:
                image['url'] = BASE_URL + url_for('patient_cases_api.getImage', case_id = response['case_id'], index_1 = i, index_2 = j)
                j+=1
            i+=1
        return jsonify(response)
    #jsonify(result.invalidFiles)


'''
NORMAL IMAGES

'''


#get all the images in a case
@case_bp.route('/<case_id>/images/', methods=['GET'])
def getAllCaseImages(case_id):
    result = {
        'error' : {}
        }
    #if username is in session then the call is web call, so use that username
    if 'username' in session and len(session['username']) > 0:
        username = session['username']
    else:
        if 'key' not in request.args or len(request.args['key']) == 0:
            result['error']['error'] = True
            result['error']['error_msgessage'] = "key not specified"
            return jsonify(result)

        auth_result = Auth.checkKeyValidity(request.args['key'])

        if not auth_result['valid']:
            result['error']['error'] = True
            result['error']['error_msgessage'] = "key not valid"
            return jsonify(result)

        username = auth_result['username']

    if not PatientCases.userHasAuthentication(case_id, username):
        result['error']['error'] = True
        result['error']['error_msgessage'] = "logged in user do not have permission to acccess this case"
        return jsonify(result)

    case_result = PatientCases.findCase(case_id)

    if case_result == None:
        result['error']['error'] = True
        result['error']['error_msgessage'] = "Case id not valid"
        return jsonify(result)

    #Now that the authentication is done process the result and respond according to the api refference
    #take the files from the case result
    files =  case_result['files']
    result['error']['error'] = False
    result['images'] = []
    i = 0 #to keep track of index_1
    for file in files:
        series = {}
        series['series_description'] = file['series_description']
        series['series_time'] = file['series_time']
        series['images'] = []
        j = 0 #to keep track of index_2
        for image in file['images']:
            img = {}
            img['filename'] = image['org_filename']
            img['url'] = BASE_URL + url_for('patient_cases_api.getImage', case_id = case_id, index_1 = i, index_2 = j)
            j+=1
            series['images'].append(img)
        i+=1
        result['images'].append(series)

    return jsonify(result)



#get the no of serries in a case
@case_bp.route('/<case_id>/images/count', methods=['GET'])
def getSeriesCount(case_id):
    result = {
        'error' : {}
        }
    #if username is in session then the call is web call, so use that username
    if 'username' in session and len(session['username']) > 0:
        username = session['username']
    else:
        if 'key' not in request.args or len(request.args['key']) == 0:
            result['error']['error'] = True
            result['error']['error_msgessage'] = "key not specified"
            return jsonify(result)

        auth_result = Auth.checkKeyValidity(request.args['key'])

        if not auth_result['valid']:
            result['error']['error'] = True
            result['error']['error_msgessage'] = "key not valid"
            return jsonify(result)

        username = auth_result['username']

    if not PatientCases.userHasAuthentication(case_id, username):
        result['error']['error'] = True
        result['error']['error_msgessage'] = "logged in user do not have permission to acccess this case"
        return jsonify(result)

    case_result = PatientCases.findCase(case_id)

    if case_result == None:
        result['error']['error'] = True
        result['error']['error_msgessage'] = "Case id not valid"
        return jsonify(result)

    result['error']['error'] = False
    result['count'] = len(case_result['files'])

    return jsonify(result)



#get all the images in a series
@case_bp.route('/<case_id>/images/<int:index_1>/', methods=['GET'])
def getSeriesImages(case_id,index_1):
    result = {
        'error' : {}
        }
    #if username is in session then the call is web call, so use that username
    if 'username' in session and len(session['username']) > 0:
        username = session['username']
    else:
        if 'key' not in request.args or len(request.args['key']) == 0:
            result['error']['error'] = True
            result['error']['error_msgessage'] = "key not specified"
            return jsonify(result)

        auth_result = Auth.checkKeyValidity(request.args['key'])

        if not auth_result['valid']:
            result['error']['error'] = True
            result['error']['error_msgessage'] = "key not valid"
            return jsonify(result)

        username = auth_result['username']

    if not PatientCases.userHasAuthentication(case_id, username):
        result['error']['error'] = True
        result['error']['error_msgessage'] = "logged in user do not have permission to acccess this case"
        return jsonify(result)

    series_result = PatientCases.findSeries(case_id, index_1)

    if series_result == None:
        result['error']['error'] = True
        result['error']['error_msgessage'] = "Case id not valid"
        return jsonify(result)

    result['error']['error'] = False
    result['images'] = []
    i = 0

    for image in series_result['images']:
        img = {}
        img['filename'] = image['org_filename']
        img['url'] = BASE_URL + url_for('patient_cases_api.getImage', case_id = case_id, index_1 = index_1, index_2 = i)
        i += 1
        result['images'].append(img)

    return jsonify(result)



#get image count in a series
@case_bp.route('/<case_id>/images/<int:index_1>/count', methods=['GET'])
def getImageCount(case_id,index_1):
    result = {
        'error' : {}
        }
    #if username is in session then the call is web call, so use that username
    if 'username' in session and len(session['username']) > 0:
        username = session['username']
    else:
        if 'key' not in request.args or len(request.args['key']) == 0:
            result['error']['error'] = True
            result['error']['error_msgessage'] = "key not specified"
            return jsonify(result)

        auth_result = Auth.checkKeyValidity(request.args['key'])

        if not auth_result['valid']:
            result['error']['error'] = True
            result['error']['error_msgessage'] = "key not valid"
            return jsonify(result)

        username = auth_result['username']

    if not PatientCases.userHasAuthentication(case_id, username):
        result['error']['error'] = True
        result['error']['error_msgessage'] = "logged in user do not have permission to acccess this case"
        return jsonify(result)

    series_result = PatientCases.findSeries(case_id, index_1)

    if series_result == None:
        result['error']['error'] = True
        result['error']['error_msgessage'] = "Case id not valid"
        return jsonify(result)

    result['error']['error'] = False
    result['count'] = len(series_result['images'])

    return jsonify(result)



#Get a single image
@case_bp.route('/<case_id>/images/<int:index_1>/<int:index_2>', methods=['GET'])
def getImage(case_id,index_1,index_2):
    #if username is in session then the call is web call, so use that username
    if 'username' in session and len(session['username']) > 0:
        username = session['username']
    elif 'key' not in request.args or len(request.args['key']) == 0:
        abort(403)
        return ""
    else:
        auth_result = Auth.checkKeyValidity(request.args['key'])
        if not auth_result['valid']:
            abort(403)
            return ""
        username = auth_result['username']

    if not PatientCases.userHasAuthentication(case_id, username):
        abort(403)
        return ""

    #TODO get the buffer from a controller module and send it to the Response


    f = PatientCases.findImage(case_id, index_1, index_2)
    if f == None:
        return abort(404)

    buffer = Conversions(f['disk_filename']).dicomToImage()
    return Response(buffer, mimetype='image/jpeg')




'''
RI MAPPED IMAGES

'''

#get all the RI mapped images in a case
@case_bp.route('/<case_id>/ri-map/', methods=['GET'])
def getAllCaseRiImages(case_id):
    result = {
        'error' : {}
        }
    #if username is in session then the call is web call, so use that username
    if 'username' in session and len(session['username']) > 0:
        username = session['username']
    else:
        if 'key' not in request.args or len(request.args['key']) == 0:
            result['error']['error'] = True
            result['error']['error_msgessage'] = "key not specified"
            return jsonify(result)

        auth_result = Auth.checkKeyValidity(request.args['key'])

        if not auth_result['valid']:
            result['error']['error'] = True
            result['error']['error_msgessage'] = "key not valid"
            return jsonify(result)

        username = auth_result['username']

    if not PatientCases.userHasAuthentication(case_id, username):
        result['error']['error'] = True
        result['error']['error_msgessage'] = "logged in user do not have permission to acccess this case"
        return jsonify(result)

    case_result = PatientCases.findCase(case_id)

    if case_result == None:
        result['error']['error'] = True
        result['error']['error_msgessage'] = "Case id not valid"
        return jsonify(result)

    #we will not take any image into consideration which is not "t2"

    #Now that the authentication is done process the result and respond according to the api refference
    #take the files from the case result
    files =  case_result['files']
    result['error']['error'] = False
    result['images'] = []
    i = 0 #to keep track of index_1
    for file in files:
        series = {}
        series['series_description'] = file['series_description']
        series['series_time'] = file['series_time']
        series['images'] = []
        if 't2' not in series['series_description'] and 'T2' not in series['series_description']:
            #case_result['files'].remove(series)
            series['ri_mapable'] = False
        else:
            series['ri_mapable'] = True
            j = 0 #to keep track of index_2
            for image in file['images']:
                img = {}
                img['filename'] = image['org_filename']
                img['url'] = BASE_URL + url_for('patient_cases_api.getRiMappedImage', case_id = case_id, index_1 = i, index_2 = j)
                j+=1
                series['images'].append(img)
        i+=1
        result['images'].append(series)

    return jsonify(result)

#get all the RI mapped images in a series
@case_bp.route('/<case_id>/ri-map/<int:index_1>/', methods=['GET'])
def getSeriesRiImages(case_id,index_1):
    result = {
        'error' : {}
        }
    #if username is in session then the call is web call, so use that username
    if 'username' in session and len(session['username']) > 0:
        username = session['username']
    else:
        if 'key' not in request.args or len(request.args['key']) == 0:
            result['error']['error'] = True
            result['error']['error_msgessage'] = "key not specified"
            return jsonify(result)

        auth_result = Auth.checkKeyValidity(request.args['key'])

        if not auth_result['valid']:
            result['error']['error'] = True
            result['error']['error_msgessage'] = "key not valid"
            return jsonify(result)

        username = auth_result['username']

    if not PatientCases.userHasAuthentication(case_id, username):
        result['error']['error_msgessage'] = "logged in user do not have permission to acccess this case"
        return jsonify(result)

    series_result = PatientCases.findSeries(case_id, index_1)

    if series_result == None:
        result['error']['error'] = True
        result['error']['error_msgessage'] = "Case id not valid"
        return jsonify(result)

    if 't2' not in series_result['series_description'] and 'T2' not in series_result['series_description']:
        result['error']['error'] = True
        result['error']['error_msgessage'] = "The series selected is not a T2 series. Cannot be RI mapped"
        return jsonify(result)

    result['error']['error'] = False
    result['images'] = []

    i = 0
    for image in series_result['images']:
        img = {}
        img['filename'] = image['org_filename']
        img['url'] = BASE_URL + url_for('patient_cases_api.getRiMappedImage', case_id = case_id, index_1 = index_1, index_2 = i)
        i += 1
        result['images'].append(img)

    return jsonify(result)

#get single RI mapped image
@case_bp.route('/<case_id>/ri-map/<int:index_1>/<int:index_2>', methods=['GET'])
def getRiMappedImage(case_id,index_1,index_2):
    #if username is in session then the call is web call, so use that username
    if 'username' in session and len(session['username']) > 0:
        username = session['username']
    elif 'key' not in request.args or len(request.args['key']) == 0:
        abort(403)
        return ""
    else:
        auth_result = Auth.checkKeyValidity(request.args['key'])
        if not auth_result['valid']:
            abort(403)
            return ""
        username = auth_result['username']

    if not PatientCases.userHasAuthentication(case_id, username):
        abort(403)
        return ""

    #TODO get the ri-buffer from a controller module and send it to the Response

    #for testing only
    f = PatientCases.findImage(case_id, index_1, index_2)
    if f == None:
        abort(404)
    buffer = Conversions(f['disk_filename']).dicomToRIColoredImage()
    return Response(buffer, mimetype='image/jpeg')


'''
Image Analysis
'''

#temporary solution
@case_bp.route("/<case_id>/images/<int:index_1>/<int:index_2>/analysis")
def analyseSingleImage(case_id, index_1, index_2):
    result = {'error':{
        'error': False
    }}
    #if username is in session then the call is web call, so use that username
    if 'username' in session and len(session['username']) > 0:
        username = session['username']
    elif 'key' not in request.args or len(request.args['key']) == 0:
        abort(403)
        return ""
    else:
        auth_result = Auth.checkKeyValidity(request.args['key'])
        if not auth_result['valid']:
            abort(403)
            return ""
        username = auth_result['username']

    if not PatientCases.userHasAuthentication(case_id, username):
        abort(403)
        return ""


    f = PatientCases.findImage(case_id, index_1, index_2)
    if f == None:
        return abort(404)

    result['error']['error'] = False

    if 're_analysis' not in request.args or request.args['re_analysis'] == 'false':
        analysis = AnalysisResult.findByCase(case_id, index_1, index_2)
        if analysis == None:
            flag = True
        else:
            analysis['error'] = result['error']
            analysis['analysis_image'] = BASE_URL + url_for('patient_cases_api.analysisImage',
                                                          case_id=case_id,
                                                          index_1 = index_1,
                                                          index_2 = index_2,
                                                          analysis_id = str(analysis['_id']))

            #pop fields that are not required as response to api
            analysis_index = 0
            for infected_area in analysis['infected_areas']:
                #pop fields that are not required as response to api
                infected_area.pop('points')
                infected_area.pop('box_width')
                infected_area.pop('box_height')
                #add the update url
                infected_area['update_actual_result_url'] = BASE_URL + url_for('patient_cases_api.uploadAnlysis',
                                                                        case_id=case_id,
                                                                        index_1 = index_1,
                                                                        index_2 = index_2,
                                                                        analysis_id = str(analysis['_id']),
                                                                        analysis_index = analysis_index)
                analysis_index += 1
            #pop fields that are not required as response to api
            analysis.pop('_id')
            analysis.pop('case_id')
            analysis.pop('index_1')
            analysis.pop('index_2')
            return jsonify(analysis)
    else:
        flag = True

    if flag:
        dicom = Conversions(f['disk_filename'])
        cluster = SingleClusterer(dicom)

        result['infected_areas'] = []
        infected_areas = []

        AnalysisResult.delete(case_id, index_1, index_2)

        for _disease_key in cluster.diseases.keys():
            disease_clusters = cluster.diseases_clusters[_disease_key]
            if len(disease_clusters.keys()) > 0:
                for disease_cluster_key in disease_clusters.keys():
                    c = disease_clusters[disease_cluster_key]
                    c.compute()
                    #c.searchForDiseases()
                    i_area = {}
                    i_area['detected_result'] = _disease_key
                    i_area['coordinate'] = c.p1
                    i_area['area'] = c.getTightArea()
                    i_area['tumor_width'] = c.tumorwidth
                    i_area['tumor_height'] = c.tumorheight
                    i_area['average_chemical_composition'] = {'x':(0,0.5,0.8,1.3,1.4,1.5,1.6,1.8,2,2.4,2.6,2.8,3,3.2,3.4,3.6,3.7,3.9,4,4.4),
                    'y':c.getAverageChemicalComposition(),
                    'labels':('','','LIP','','LAC','','','','NAA','GLM','','','CR','','CHO','','MI','','CR2','')}
                    infected_areas.append(InfectedAreas((c.p1[0],c.p1[1]),
                                                        c.getWidth(),
                                                        c.getHeight(),
                                                        c.tumorwidth,
                                                        c.tumorheight,
                                                        i_area['average_chemical_composition'],
                                                        c.getArea(),
                                                        _disease_key,
                                                        c.elements))

                    result['infected_areas'].append(i_area)

                #result['diseases'].append(disease)

        if len(infected_areas) != 0:
            analysisResult = AnalysisResult(case_id, index_1, index_2, infected_areas)
            analysis_id = analysisResult.save()
            result['analysis_image'] = BASE_URL + url_for('patient_cases_api.analysisImage',
                                                          case_id=case_id,
                                                          index_1 = index_1,
                                                          index_2 = index_2,
                                                          analysis_id = analysis_id)

    analysis_index = 0
    for infected_area in result['infected_areas']:
        infected_area['update_actual_result_url'] = BASE_URL + url_for('patient_cases_api.uploadAnlysis',
                                                                case_id=case_id,
                                                                index_1 = index_1,
                                                                index_2 = index_2,
                                                                analysis_id = analysis_id,
                                                                analysis_index = analysis_index)
        analysis_index+=1

    return jsonify(result)


@case_bp.route('/<case_id>/<int:index_1>/<int:index_2>/analyis-image/<analysis_id>')
def analysisImage(case_id, index_1, index_2, analysis_id):
    res = AnalysisResult.find(analysis_id, case_id, index_1, index_2)
    if res == None:
        return abort(404)

    res.pop('_id', None)

    f = PatientCases.findImage(case_id, index_1, index_2)
    if f == None:
        return abort(404)

    filename = f['disk_filename']
    boxes = []
    for infected_area in res['infected_areas']:
        coordinate = infected_area['coordinate']
        tumor_size = (infected_area['box_height'], infected_area['box_width'])
        points = infected_area['points']
        rgb = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
        boxes.append((coordinate, tumor_size,rgb, [(150,150), [150,151]]))
    buffer = Segment(filename, boxes).drawBox()
    return  Response(buffer, mimetype='image/jpeg')

'''
Upload Analysis
'''

@case_bp.route('/<case_id>/<int:index_1>/<int:index_2>/analysis/<analysis_id>/<int:analysis_index>/upload-analysis',methods=['POST'])
def uploadAnlysis(case_id, index_1, index_2, analysis_id, analysis_index):
        response = { "error"  : {} }
        #if username is in session then the call is web call, so use that username
        if 'username' in session and len(session['username']) > 0:
            username = session['username']
        else:
            if 'key' not in request.form or len(request.form['key']) == 0:
                response['error']['error'] = True
                response['error']['error_message'] = "key not specified"
                return jsonify(response)

            auth_result = Auth.checkKeyValidity(request.form['key'])

            if not auth_result['valid']:
                response['error']['error'] = True
                response['error']['error_message'] = "key not valid"
                return jsonify(response)

            username = auth_result['username']

        if 'actual_result' not in request.form or len(request.form['actual_result']) == 0:
            response['error']['error'] = True
            response['error']['error_message'] = "field actual_result is not present"
            return jsonify(response)


        actual_result = request.form['actual_result']
        if actual_result not in ['normal','csf','edma','MS','cyst','glioma','glioblastoma','lymphoma','metastesis']:
            response['error']['error'] = True
            response['error']['error_message'] = "actual_result not valid"
            return jsonify(response)

        res = AnalysisResult.setActualResult(analysis_id, analysis_index, actual_result)
        if res == True:
            response['error']['error'] = False
            return jsonify(response)
        else:
            response['error']['error'] = True
            response['error']['error_message'] = "analysis id might be invalid"
            return jsonify(response)
