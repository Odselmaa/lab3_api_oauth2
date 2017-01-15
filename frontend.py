from flask import Flask, redirect, session as client_session, request, render_template
from pymongo import MongoClient
import httplib2
import json
from custom_response import *
from datetime import timedelta, datetime
from flask_session import Session
from functools import wraps
from collections import Counter


app = Flask(__name__)
SESSION_TYPE = 'mongodb'
app.config.from_object(__name__)
Session(app)

clientDb = MongoClient('mongodb://localhost:27017/')
db = clientDb.rsoi

CLIENT_ID = 'nmmqo1yI2rjyXfmEJiupzsLFSOX3i5MlMF5IgHpjMjpdy4IPGc.apps.myserver.com'
CLIENT_SECRET = 'Gd3QKuzPHZzOoi04R0gTzy7MjVm0SR'
REDIRECT_URI = 'http://localhost:5001/oauth2callback'
PAGE = 1
SIZE = 3

AUTH_FRONTEND_URL = 'http://localhost:5002/'
GOOD_SERVICE_URL = 'http://localhost:5004/'
ORDER_SERVICE_URL = 'http://localhost:5005/'
AUTH_SERVICE_URL = 'http://localhost:5007/'

def check_authorization(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        access_token = client_session.get('access_token', None)
        refresh_token = client_session.get('refresh_token', None)
        if access_token and refresh_token:
            url = AUTH_SERVICE_URL + 'check_authorization/%s' % access_token
            h = httplib2.Http()
            result = h.request(url, 'GET')
            response = json.loads(result[1])
            print(result)
            client_session['logged'] = True
            if response.get("error", None) is not None:
                url = AUTH_SERVICE_URL + 'oauth2/token?refresh_token=%s&grant_type=%s' % (refresh_token,
                                                                                          'refresh_token')
                h = httplib2.Http()
                result = h.request(url, 'GET')
                print("Response fron Authorization server: " + (json.dumps(result[1])))
                token_result = json.loads(result[1])
                if token_result.get('error', None) is not None:
                    return json.dumps(token_result)
                else:
                    client_session['access_token'] = token_result['access_token']
                    return f(*args, **kwargs)
            return f(*args, **kwargs)
        else:
            return authorize()

    return decorated_function


def get_goods(page=PAGE, size=SIZE):
    url = GOOD_SERVICE_URL + 'goods/?page=%d&size=%d' % (page, size)
    h = httplib2.Http()
    result = h.request(url, 'GET')
    goods = result[1]
    return json.loads(goods)


@check_authorization
def get_orders_items():
    headers = {'Authorization': 'Bearer ' + client_session['access_token']}
    url = ORDER_SERVICE_URL + 'orders/items'
    h = httplib2.Http()
    result = h.request(url, 'GET', headers=headers)
    print(result)
    if result[0]['status'] == "200":
        return json.loads(result[1])
    else:
        return None


@app.route('/orders')
@check_authorization
def get_orders_info():
    print(client_session['access_token'])
    headers = {'Authorization': 'Bearer ' + client_session['access_token']}
    url = ORDER_SERVICE_URL + 'orders?page=1&size=1'
    h = httplib2.Http()
    result = h.request(url, 'GET', headers=headers)
    orders = {}
    if result[0]['status'] == '200':
        orders = json.loads(result[1])
        print(orders)

    for order in orders:
        created_when = order['created_when']
        order['created_when'] = datetime.fromtimestamp(created_when / 1000.0).strftime('%Y-%m-%d %H:%M')

        if order['billing_info'] == []:
            order['billing_info'] = 'N/A'
        else:
            order['billing_info'] = order['billing_info'][0]['city'] + " " + \
                                    order['billing_info'][0]['address'] + " " + \
                                    order['billing_info'][0]['zip']

    logged = client_session.get('logged', False)
    return render_template('client_order.html', orders=orders, logged=logged)


@app.route('/order/<int:order_id>')
@check_authorization
def get_order(order_id=None):
    if order_id:
        url = ORDER_SERVICE_URL + 'order/' + str(order_id)
        h = httplib2.Http()
        headers = {'Authorization': 'Bearer ' + client_session['access_token']}
        result = h.request(url, 'GET', headers=headers)
        order = json.loads(result[1])[0]
        logged = client_session.get('logged', True)
        return render_template('client_order_current.html', order=order, logged=logged)
    else:
        pass


@app.route('/order/<int:order_id>/good/<int:good_id>')
@check_authorization
def add_good_order(order_id, good_id):
    if order_id is not None and good_id is not None:
        url = ORDER_SERVICE_URL + 'order/{}/good/{}'.format(order_id, good_id)
        h = httplib2.Http()
        headers = {'Authorization': 'Bearer ' + client_session['access_token']}
        result = h.request(url, 'POST', headers=headers)
        response = json.loads(result[1])

        if response.get('error'):
            return json.dumps({'error':"Order doesn't exist"}), 404
        return redirect('/')

    else:
        pass


def get_count():
    url = GOOD_SERVICE_URL + 'goods/count'
    h = httplib2.Http()
    result = h.request(url, 'GET')
    count = result[1]
    return json.loads(count)


@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        per_page = request.values.get('per_page', 3)
        per_page = int(per_page)
        client_session['size'] = per_page
    logged = client_session.get('logged', False)
    client_session['current_page'] = 1
    size = client_session.get('size', SIZE)
    goods = get_goods(page=PAGE, size=size)

    orders = []
    if logged:
        orders = get_orders_items()
        print(type(orders))
        if orders is None or type(orders)!=list:
            orders = []

    count_json = get_count()
    count = count_json['count']
    pages = int(count / size)
    if count % size != 0 and (count > size or count < size):
        pages += 1
    current_page = client_session.get('current_page', 1)
    return render_template("client_index.html",
                           logged=logged,
                           goods=goods,
                           pages=pages,
                           current_page=current_page,
                           size=size,
                           orders=orders
                           )


@app.route('/pages/<int:page_number>')
def get_goods_by_page(page_number):
    access_token = client_session.get('access_token')
    if access_token:
        logged = True
    else:
        logged = False
    size = client_session.get('size', SIZE)
    goods = get_goods(page=page_number, size=size)
    count_json = get_count()
    count = count_json['count']
    pages = int(count / size)
    if count % size != 0 and (count > size or count < size):
        pages += 1

    client_session['current_page'] = page_number
    return render_template("client_index.html",
                           logged=logged,
                           goods=goods,
                           pages=pages,
                           current_page=page_number,
                           size=size)


@app.route('/me')
@check_authorization
def get_my_info():
    if client_session.get('name') is None:
        headers = {'Authorization': 'Bearer ' + client_session['access_token']}
        url = AUTH_SERVICE_URL + 'me'
        h = httplib2.Http()
        result = h.request(url, 'GET', headers=headers)
        if result[0]['status'] == '200':
            my_info = json.loads(result[1])
            client_session['name'] = my_info['name']
            client_session['email'] = my_info['email']
            client_session['gender'] = my_info['gender']
            client_session['user_id'] = my_info['_id']['$oid']

    name = client_session.get('name')
    email = client_session.get('email')
    gender = client_session.get('gender')
    logged = client_session.get('logged', False)
    return render_template('client_me.html', name=name, email=email, gender=gender, logged=logged)


@app.route('/login')
@check_authorization
def login():
    return redirect('/')


def authorize():
    return redirect(
        (AUTH_FRONTEND_URL + 'oauth2?client_id={0}&redirect_uri={1}&response_type=code'.format(
            CLIENT_ID, REDIRECT_URI)))


@app.route('/oauth2callback')
def oauth2callback():
    code = request.values.get('code')
    if code:
        url = AUTH_SERVICE_URL + 'oauth2/token?code=' + code
        h = httplib2.Http()
        result = h.request(url, 'GET')
        print(result)
        token_result = json.loads(result[1])

        access_token = token_result.get('access_token')
        refresh_token = token_result.get('refresh_token')
        if access_token:
            client_session['refresh_token'] = refresh_token
            client_session['access_token'] = access_token
            client_session['logged'] = True

            headers = {'Authorization': 'Bearer ' + client_session['access_token']}
            url = AUTH_SERVICE_URL + 'me'
            h = httplib2.Http()
            result = h.request(url, 'GET', headers=headers)
            if result[0]['status'] == '200':
                my_info = json.loads(result[1])
                client_session['name'] = my_info['name']
                client_session['email'] = my_info['email']
                client_session['gender'] = my_info['gender']
                client_session['user_id'] = my_info['_id']['$oid']

        return redirect('/')

    error = request.values.get('error')
    if error:
        return json.dumps({ERROR: ACCESS_DENIED}, indent=4), 400


@app.route('/logout')
def log_out():
    logged = client_session.get('logged', False)
    if logged:
        del client_session['logged']
    return redirect('/')


@app.before_request
def make_session_permanent():
    client_session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=60)


if __name__ == '__main__':
    app.secret_key = "1212000011"
    app.run(port=5001)
