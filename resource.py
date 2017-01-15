from pymongo import MongoClient
from flask import render_template, request, Flask, session as resource_session
from functools import wraps
import json
from bson.json_util import dumps

from TableController import GoodController
from TableController import UserController
from TableController import OrderController
from TableController import BillingController

from Models import Billing
from Models import Order

from custom_response import *
import time

from TableController.Properties import *


client = MongoClient('mongodb://localhost:27017/')
db = client['rsoi']
app = Flask(__name__)



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

        # expiration_date = result[EXPIRATION_DATE]
        # print(str(expiration_date))
        # print(str(now_date))
        #
        # if expiration_date < now_date:
        #     return json.dumps({ERROR: INVALID_TOKEN, ERROR_DESC:INVALID_TOKEN_DESC}), 400

        return f(*args, **kwargs)

    return decorated_function


@app.route('/goods/', methods=['GET'])
@app.route('/goods/<int:good_id>', methods=['GET'])
def get_good(good_id=None):
    if id:
        good = goodCnt.getGood(good_id)
        return json.dumps(json.loads(dumps(good)), indent=4)
    else:
        page = int(request.args.get('page'))
        size = int(request.args.get('size'))
        page = (page - 1) * size
        goods = goodCnt.getGoodAll(page, size)
        return json.dumps(json.loads(dumps(goods)), indent=4)


@app.route('/me')
@login_required
def get_me():
    user_info = userCtrl.getUserByToken(resource_session.get('access_token'))
    return json.dumps(json.loads(dumps(user_info)), indent=4)


@app.route('/orders', methods=['GET'])
@login_required
def get_orders():
    page = (request.args.get('page'))
    size = (request.args.get('size'))
    if page is None or size is None:
        return "Please specify parameters", 400

    page = int(page)
    size = int(size)
    page = (page - 1) * size
    print(page)
    print(size)
    if size:
        return json.dumps(json.loads(dumps(orderCtrl.get_orders_info(page, size))), indent=4)
    else:
        return "PLease specify all fields", 400


@app.route('/order/<int:order_id>', methods=['GET', 'PATCH'])
@login_required
def get_patch_order_by_id(order_id=None):
    if id is None:
        pass

    if request.method == 'GET':
        # order_info = json.loads(dumps(orderCtrl.getOrderInfo(id)))
        order = json.loads(dumps(orderCtrl.get_order(order_id)))
        good_ids = order['good_ids']
        goods = json.loads(dumps(goodCnt.getGoodByIds(good_ids)))
        del order['good_ids']
        order['goods'] = goods

        if order.get('bill_id'):
            bill_id = str(order['bill_id'])
            print(str(bill_id))
            del order['bill_id']
            bill = json.loads(dumps(billCtrl.getBillingByObject(bill_id)))
            order['bill'] = bill

        return json.dumps(order, indent=4)
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

    order = Order(id=order_id, user_id=resource_session['user_id'])
    return "Order with id=" + dumps(orderCtrl.create_order(order)) + " created"


@app.route('/order/<int:order_id>/good/<int:good_id>', methods=['POST', 'DELETE'])
@login_required
def manage_good_order(order_id, good_id):
    if request.method == 'POST':
        return dumps(orderCtrl.add_good(order_id=order_id, good_id=good_id))
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


@app.route('/index')
def get_main_page():
    return render_template('client_index.html')


def verify_access_token(access_token):
    print(userCtrl.verify_access_token(access_token))
    return userCtrl.verify_access_token(access_token) == 1


if __name__ == '__main__':
    goodCnt = GoodController(db)
    userCtrl = UserController(db)
    orderCtrl = OrderController(db)
    billCtrl = BillingController(db)
    app.secret_key = "0003"
    app.run(port=5003)
