from flask import Flask, request, redirect
import random
import string
import json
from bson.json_util import dumps
from pymongo import MongoClient
import jwt

from TableController import ClientController
from TableController import UserController

from Models import User
import time

from custom_response import *
from TableController.Properties import *
from functools import wraps

app = Flask(__name__)

clientDb = MongoClient('mongodb://localhost:27017/')
db = clientDb.rsoi
clientCtrl = ClientController(db)
userCtrl = UserController(db)

CODE = 'code'
REDIRECT_URI = 'redirect_uri'
EXPIRATION_TIME = 180  # SECONDS



def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = (request.headers.get('Authorization'))
        if auth_header is None:
            return json.dumps({ERROR: AUTHORIZATION_REQUIRED}), 401
        bearer, access_token = auth_header.split()
        if bearer != 'Bearer' or verify_access_token(access_token) is False:
            return json.dumps({ERROR: AUTHORIZATION_REQUIRED}), 401
        result = json.loads(dumps(userCtrl.get_user_grant(access_token)))
        now_date = int(round(time.time() * 1000))
        expiration_date = result[EXPIRATION_DATE]
        if expiration_date < now_date:
            return json.dumps({ERROR: INVALID_TOKEN, ERROR_DESC: INVALID_TOKEN_DESC}), 400
        return f(*args, **kwargs)
    return decorated_function


@app.route('/oauth2')
def oauth2():
    client_id = request.values['client_id']
    response_type = request.values['response_type']
    redirect_uri = request.values['redirect_uri']

    if client_id and response_type and redirect_uri:
        if clientCtrl.getClientById(client_id):
            if response_type == 'code':
                return json.dumps({SUCCESS: VALID_CLIENT}), 200
            else:
                return json.dumps({ERROR: INVALID_REQUEST, ERROR_DESC: INVALID_RESPONSE_TYPE_DESC}), 400
        else:
            return json.dumps({ERROR: UNAUTHORIZED_CLIENT, ERROR_DESC: UNAUTHORIZED_CLIENT_DESC}), 401
    else:
        return json.dumps({ERROR: INVALID_REQUEST, ERROR_DESC: INVALID_REQUEST_DESC}), 400


@app.route('/oauth2/code')
def oauth2_code():
    username = request.values['username']
    if username:
        code = ''.join(
            random.choice(string.ascii_uppercase + string.digits + string.lowercase) for _ in range(40))
        result = userCtrl.addCode(User(name=username, code=code))
        result = json.loads(dumps(result))
        if result.get('errmsg') is None:
            return json.dumps({'code': code}), 200
        else:
            return json.dumps({'error': result}), 400
    else:
        return json.dumps({ERROR: INVALID_REQUEST, ERROR_DESC: INVALID_USER_DESC}), 401


@app.route('/oauth2/token')
def get_token():
    code = request.args.get('code')
    refresh_token = request.args.get('refresh_token')
    if code:
        user = userCtrl.get_user_by_code(code)
        if user is None:
            return json.dumps({ERROR: INVALID_REQUEST, ERROR_DESC: INVALID_REQUEST_DESC}), 400
        else:
            user = json.loads(dumps(user))
            print(user)

            access_token = ''.join(
                random.choice(string.ascii_uppercase + string.digits + string.lowercase) for _ in range(50))
            refresh_token = ''.join(
                random.choice(string.ascii_uppercase + string.digits + string.lowercase) for _ in range(40))
            expiration_date = int(round(time.time() * 1000)) + EXPIRATION_TIME * 1000

            user = User(name=user["name"],
                        code=None,
                        access_token=access_token,
                        refresh_token=refresh_token,
                        expiration_date=expiration_date,
                        expires=EXPIRATION_TIME)
            result = userCtrl.addTokens(user)
            result = json.loads(dumps(result))
            return json.dumps(result)
    elif refresh_token:
        user = userCtrl.get_user_by_refresh_token(refresh_token)
        user = json.loads(dumps(user))
        if user is None:
            return json.dumps({ERROR: INVALID_REQUEST, ERROR_DESC: INVALID_REQUEST_DESC}), 400
        grant_type = request.values.get('grant_type')
        if grant_type == 'refresh_token':
            access_token = ''.join(
                random.choice(string.ascii_uppercase + string.digits + string.lowercase) for _ in range(50))
            expiration_date = int(round(time.time() * 1000)) + EXPIRATION_TIME * 1000
            user = User(name=user["name"],
                        code=None,
                        access_token=access_token,
                        refresh_token=refresh_token,
                        expiration_date=expiration_date,
                        expires=EXPIRATION_TIME)
            result = userCtrl.addTokens(user)
            result = json.loads(dumps(result))
            return json.dumps(result)
        else:
            return json.dumps({ERROR: UNSUPPORTED_GRANT_TYPE, ERROR_DESC: UNSUPPORTED_GRANT_TYPE_DESC}), 400
    else:
        return json.dumps({ERROR: INVALID_REQUEST, ERROR_DESC: INVALID_REQUEST_DESC}), 400


def verify_access_token(access_token):
    return userCtrl.verify_access_token(access_token) == 1


@app.route('/check_authorization/<string:access_token>')
def check_authorization(access_token):

    if verify_access_token(access_token) is False:
        return json.dumps({ERROR: AUTHORIZATION_REQUIRED}), 401
    else:
        result = json.loads(dumps(userCtrl.get_user_grant(access_token)))
        now_date = int(round(time.time() * 1000))
        expiration_date = result[EXPIRATION_DATE]
        if expiration_date <= now_date:
            return json.dumps({ERROR: INVALID_TOKEN, ERROR_DESC: INVALID_TOKEN_DESC}), 400
        else:
            return json.dumps({'response': 'successful'}), 200


@app.route('/me')
@login_required
def getMe():
    auth_header = (request.headers.get('Authorization'))
    if auth_header is None:
        return json.dumps({ERROR: AUTHORIZATION_REQUIRED}), 401
    bearer, access_token = auth_header.split()
    user_info = userCtrl.get_user_info(access_token)
    return (dumps(user_info))


if __name__ == '__main__':
    app.secret_key = "98123"
    app.run(port=5007)
