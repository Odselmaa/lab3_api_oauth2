from flask import Flask, redirect, session as auth_session, request, render_template
import random
import string
import json
from bson.json_util import dumps
from pymongo import MongoClient
import jwt
import httplib2
from TableController import ClientController
from TableController import UserController

from Models import User
from Models import Client
import time
from flask_session import Session

from custom_response import *
import custom_response
from functools import wraps


app = Flask(__name__)
SESSION_TYPE = 'mongodb'
app.config.from_object(__name__)
Session(app)

clientDb = MongoClient('mongodb://localhost:27017/')
db = clientDb.rsoi
clientCtrl = ClientController(db)
userCtrl = UserController(db)

CODE = 'code'
REDIRECT_URI = 'redirect_uri'
AUTH_SERVICE_URL = 'http://localhost:5007/'


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = (request.headers.get('Authorization'))

        if auth_header is None:
            return json.dumps({ERROR: AUTHORIZATION_REQUIRED}), 401
        bearer, access_token = auth_header.split()

        if bearer != 'Bearer':
            return json.dumps({ERROR: AUTHORIZATION_REQUIRED}), 401
        # sending request to UserService to check access token
        url = "http://localhost:5007/check_authorization/"+access_token
        h = httplib2.Http()
        result = h.request(url, 'GET')
        status = result[0]['status']
        if status != '200':
            return result[1], status
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def get_main():
    username = auth_session.get('username', None)
    if username:
        return render_template('auth_index.html', username=username)
    return render_template('auth_login.html')


@app.route('/credential')
def get_client():
    app_name = (auth_session.get('app_name'))
    if app_name is None:
        return "Please specify app_name", 400

    if clientCtrl.getClient(app_name) is None or clientCtrl.getClient(app_name) == []:
        client_id = ''.join(random.choice(string.ascii_uppercase + string.digits + string.lowercase) for _ in
                            range(50)) + ".apps.myserver.com"
        client_secret = ''.join(
            random.choice(string.ascii_uppercase + string.digits + string.lowercase) for _ in range(30))
        client = Client(app_name=app_name, client_id=client_id, client_secret=client_secret)
        clientCtrl.addClient(client)

        return "Hi, " + auth_session['app_name'] + " " + client_id + "\n " + client_secret + " created"
    else:
        client_result = clientCtrl.getClient(app_name)
        return dumps(client_result)


@app.route('/oauth2')
def oauth2():
    username = auth_session.get('username')
    if username:
        client_id = request.values['client_id']
        response_type = request.values['response_type']
        redirect_uri = request.values['redirect_uri']

        url = AUTH_SERVICE_URL + 'oauth2?client_id={0}&redirect_uri={1}&response_type={2}'.format(
            client_id, redirect_uri, response_type)
        h = httplib2.Http()
        result = h.request(url, 'GET')
        response = json.loads(result[1])
        error = response.get(ERROR, None)
        if error:
            error_desc = response[ERROR_DESC]
            return render_template('auth_error.html', error=response[ERROR], error_desc=error_desc)

        href = '/oauth2/approval?client_id={0}&redirect_uri={1}&response_type={2}'.format(
            client_id,
            redirect_uri,
            response_type)
        return render_template('auth_approval.html', username=username, href=href)
    else:
        return redirect('/login')


@app.route('/oauth2/approval', methods=['GET'])
def oauth2approval():
    client_id = request.values['client_id']
    response_type = request.values['response_type']
    redirect_uri = request.values['redirect_uri']
    username = auth_session['username']
    if client_id and response_type == 'code' and redirect_uri:
        url = AUTH_SERVICE_URL + 'oauth2/code?username={0}'.format(username)
        h = httplib2.Http()
        result = h.request(url, 'GET')
        response = json.loads(result[1])
        code = response.get('code')
        if code is not None:
            return redirect(redirect_uri+"?code="+code)
        else:
            error_desc = response.get('error')
            return render_template('auth_error.html', error='error', error_desc=error_desc)
    else:
        return render_template('auth_error.html', error=INVALID_REQUEST,
                               error_desc=INVALID_RESPONSE_TYPE_DESC + ": " + response_type)


@app.route('/oauth2/token')
def get_token():
    code = request.args.get('code')
    refresh_token = request.args.get('refresh_token')
    parameter = ''
    if code:
        parameter = '?code='+code
    elif refresh_token:
        parameter = '?refresh_token='+refresh_token
        parameter += '&grant_type=refresh_token'
    else:
        return render_template('auth_error.html', error=INVALID_REQUEST, error_desc=INVALID_REQUEST_DESC)

    url = AUTH_SERVICE_URL + 'oauth2/token{0}'.format(parameter)
    h = httplib2.Http()
    result = h.request(url, 'GET')
    response = json.loads(result[1])
    error = response.get(ERROR)
    if error is None:
        return json.dumps(response), 200

    error_desc = response.get(ERROR_DESC)
    return render_template('auth_error.html', error=error, error_desc=error_desc)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        if auth_session.get('username'):
            return redirect('/')
        return render_template("auth_login.html")
    elif request.method == 'POST':
        username = request.values['username']
        password = request.values['password']
        user = userCtrl.getUser(username)
        if user and password == user.password:
            print("username is %s" % username)
            auth_session['username'] = username
            return redirect('/')
        return "Username or password is incorrect"




@app.route('/logout')
def log_out():
    if auth_session.get('username', None):
        del auth_session['username']
    return redirect('/')


if __name__ == '__main__':
    app.secret_key = "98123"

    app.run(port=5002)
