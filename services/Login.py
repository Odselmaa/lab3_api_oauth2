from pymongo import MongoClient
from flask import request, Flask, session as user_service_session
from functools import wraps
import json
from bson.json_util import dumps

from custom_response import *
import time

from TableController.Properties import *

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = (request.headers.get('Authorization'))

        if auth_header is None:
            return json.dumps({ERROR: AUTHORIZATION_REQUIRED}), 401
        bearer, access_token = auth_header.split()

        if bearer != 'Bearer' or verify_access_token(access_token) is False:
            return json.dumps({ERROR: AUTHORIZATION_REQUIRED}), 401

        result = json.loads(dumps(userCtrl.getUserIdByToken(access_token)))
        now_date = int(round(time.time() * 1000))

        expiration_date = result[EXPIRATION_DATE]
        print(str(expiration_date))
        print(str(now_date))

        if expiration_date < now_date:
            return json.dumps({ERROR: INVALID_TOKEN, ERROR_DESC: INVALID_TOKEN_DESC}), 400

        return f(*args, **kwargs)

    return decorated_function