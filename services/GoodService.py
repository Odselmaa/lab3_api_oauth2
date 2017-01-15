from pymongo import MongoClient
from flask import request, Flask
import json
from bson.json_util import dumps

from TableController import GoodController

client = MongoClient('mongodb://localhost:27017/')
db = client['rsoi']
app = Flask(__name__)
goodCnt = GoodController(db)


@app.route('/goods/', methods=['GET'])
@app.route('/goods/<int:good_id>', methods=['GET'])
def get_good(good_id=None):
    if good_id:
        good = goodCnt.getGood(good_id)
        return json.dumps(json.loads(dumps(good)), indent=4)
    else:
        page = (request.args.get('page'))
        size = (request.args.get('size'))
        good_ids = request.args.get('good_ids')
        print(good_ids)
        if page is not None and size is not None:
            page = int(page)
            size = int(size)
            page = (page - 1) * size
            goods = goodCnt.getGoodAll(page, size)
            goods = json.loads(dumps(goods))
            return json.dumps(goods, indent=4)
        elif good_ids is not None:
            good_ids = list(json.loads(good_ids))
            goods = goodCnt.getGoodByIds(good_ids)
            return dumps(goods)
        else:
            return json.dumps({'error': 'parameter_error'}), 400

@app.route('/goods/count')
def get_count():
    count = goodCnt.getSize()
    return json.dumps({"count":count})


if __name__ == '__main__':
    app.secret_key = "5004004"
    app.run(port=5004)
