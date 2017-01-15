from pymongo import MongoClient
from flask import request, Flask
from functools import wraps
import json
from bson.json_util import dumps

from TableController import OrderController
from TableController import BillingController

from Models import Billing
from Models import Order

from custom_response import *
import httplib2
import requests


client = MongoClient('mongodb://localhost:27017/')
db = client['rsoi']
app = Flask(__name__)
AUTH_SERVICE_URL = 'http://localhost:5007/'
GOOD_SERVICE_URL = 'http://localhost:5004/'


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


@app.route('/orders', methods=['GET'])
@login_required
def get_orders():
    page = (request.args.get('page'))
    size = (request.args.get('size'))
    if page is None or size is None:
        return json.dumps({"error":"Please specify parameters"}), 400

    page = int(page)
    size = int(size)
    page = (page - 1) * size

    auth_header = (request.headers.get('Authorization'))
    access_token = auth_header.split()[1]

    headers = {'Authorization': 'Bearer ' + access_token}
    url = AUTH_SERVICE_URL + 'me'
    h = httplib2.Http()

    result = h.request(url, 'GET', headers=headers)
    my_info = json.loads(result[1])
    print(my_info)
    user_id = my_info['_id']['$oid']

    result = json.dumps(json.loads(dumps(orderCtrl.get_orders_info(page, size, user_id=user_id))), indent=4)
    if result:
        return result
    else:
        return json.dumps({'error': 'order_not_found'}), 404


@app.route('/orders/items', methods=['GET'])
@login_required
def get_order_items():
    auth_header = (request.headers.get('Authorization'))
    access_token = auth_header.split()[1]
    headers = {'Authorization': 'Bearer ' + access_token}
    url = AUTH_SERVICE_URL + 'me'
    h = httplib2.Http()
    result = h.request(url, 'GET', headers=headers)
    my_info = json.loads(result[1])
    print(my_info)
    user_id = my_info['_id']['$oid']
    orders = dumps(orderCtrl.get_orders(user_id))
    print(orders)
    return orders


@app.route('/order/<int:order_id>', methods=['GET', 'PATCH'])
@login_required
def get_patch_order_by_id(order_id=None):
    if id is None:
        pass

    if request.method == 'GET':
        # order_info = json.loads(dumps(orderCtrl.getOrderInfo(id)))
        # auth_header = (request.headers.get('Authorization'))
        # access_token = auth_header.split()[1]
        # headers = {'Authorization': 'Bearer ' + access_token}
        # url = USER_SERVICE_URL + 'me'
        # h = httplib2.Http()
        # result = h.request(url, 'GET', headers=headers)
        # my_info = json.loads(result[1])
        # user_id = my_info['_id']['$oid']
        #
        # order = json.loads(dumps(orderCtrl.get_order(order_id)))
        # good_ids = order['good_ids']
        # payload = {'good_ids': json.dumps(good_ids)}
        # r = requests.get(GOOD_SERVICE_URL+'goods', params=payload)
        # return r.text
        result = orderCtrl.get_order(order_id)
        if result is None:
            return json.dumps([]), 400
        else:
            return (dumps(result)),200

        # if order.get('bill_id'):
        #     bill_id = str(order['bill_id'])
        #     print(str(bill_id))
        #     bill = json.loads(dumps(billCtrl.getBillingByObject(bill_id)))
        #     order['bill'] = bill

        #return json.dumps(order, indent=4)
    elif request.method == 'PATCH':
        return str(id) + " PATCH"


@app.route('/order', methods=['POST'])
@login_required
def create_order():
    order_id = int(str(request.values.get('order_id')))
    if order_id is None:
        return "Please specify order id", 400

    if orderCtrl.check_order(order_id) > 0:
        return "Order with id = %d is already created" % order_id

    auth_header = (request.headers.get('Authorization'))
    access_token = auth_header.split()[1]
    headers = {'Authorization': 'Bearer ' + access_token}
    url = AUTH_SERVICE_URL + 'me'
    h = httplib2.Http()
    result = h.request(url, 'GET', headers=headers)
    my_info = json.loads(result[1])
    user_id = my_info['_id']['$oid']

    order = Order(order_id=order_id, user_id=user_id)
    return "Order with id=" + dumps(orderCtrl.create_order(order)) + " created"


@app.route('/order/<int:order_id>/good/<int:good_id>', methods=['POST', 'DELETE'])
@login_required
def manage_good_order(order_id, good_id):
    if request.method == 'POST':
        result = dumps(orderCtrl.add_good(order_id=order_id, good_id=good_id))
        print(result)
        if result is None:
            return json.dumps({"error":'order_not_found'}), 404
        else:
            return json.dumps({'result':'successfull'}), 200

    elif request.method == 'DELETE':
        return dumps(orderCtrl.delete_good(order_id=order_id, good_id=good_id))


@app.route('/order/<int:order_id>/billing', methods=['POST'])
@login_required
def do_billing(order_id):
    address = request.values.get('address')
    city = request.values.get('city')
    zip_num = request.values.get('zip_num')
    phone = request.values.get('phone')
    if address and city and zip_num and phone:
        billing = Billing(address=address, city=city, zip=zip_num, phone=phone)
        bill_id = json.loads(dumps(billCtrl.createBilling(billing)))
        bill_id = bill_id['$oid']
        return dumps(orderCtrl.set_billing(order_id, bill_id))
    else:
        return "Please specify all fields", 400


if __name__ == '__main__':
    orderCtrl = OrderController(db)
    billCtrl = BillingController(db)
    app.secret_key = "50050005"
    app.run(port=5005)
