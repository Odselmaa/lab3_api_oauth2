from Models import Order
from Properties import *
import pymongo
from bson.objectid import ObjectId


class OrderController:
    def __init__(self, db):
        # type: (db) -> pymongo.database.Database
        self.order_collection = db['order']

    def create_order(self, order):
        return self.order_collection.insert({ORDER_ID: order.get_id(),
                                             USER_ID: ObjectId(order.get_user_id()),
                                             GOOD_IDS: [],
                                             CREATED_WHEN: order.get_created_when()})

    def check_order(self, id):
        return self.order_collection.count({ORDER_ID: id})

    def add_good(self, order_id, good_id):
        return self.order_collection.find_one_and_update({ORDER_ID: order_id}, {'$push': {GOOD_IDS: good_id}})

    def delete_good(self, order_id, good_id):
        return self.order_collection.update({ORDER_ID: order_id}, {'$pull': {GOOD_IDS: good_id}})

    def set_billing(self, order_id, bill_id):
        return self.order_collection.find_one_and_update({ORDER_ID: order_id}, {'$set': {BILL_ID: ObjectId(bill_id)}})

    def get_order(self, order_id):
        return self.order_collection.aggregate(
            [
                {"$match": {"_id": order_id}},
                {"$unwind": "$good_ids"},
                {
                    "$lookup": {
                        "from": "good",
                        "localField": "good_ids",
                        "foreignField": "_id",
                        "as": "good_info"
                    }
                },
                {"$project": {
                    "good_info.price": 1,
                    "good_info.name": 1,
                    "good_info._id": 1,
                    "bill_id": 1,
                    "created_when": 1

                }},
                {"$unwind": "$good_info"},
                {
                    "$group": {
                        "_id": {"order_id": "$_id", "bill_id": "$bill_id", "created_when": "$created_when"},
                        "goods": {"$push": "$good_info"}
                    }
                },
                {
                    "$project":
                        {
                            "order_id": "$_id.order_id",
                            "created_when": "$_id.created_when",
                            "bill_id": "$_id.bill_id",
                            "_id": 0,
                            "goods": 1,
                        }
                },
                {
                    "$lookup": {
                        "from": "billing",
                        "localField": "bill_id",
                        "foreignField": "_id",
                        "as": "billing_info"
                    }
                }
            ]
        )

    def get_orders(self, user_id):
        return self.order_collection.aggregate(
            [
                {
                    "$match":
                        {
                            USER_ID: ObjectId(user_id)
                        }
                },
                {
                    "$project":
                        {
                            "order_id": "$_id",
                            "_id": 0,
                            "items_number": {"$size": "$good_ids"}
                        }
                }
            ]
        )

    def get_orders_info(self, skip_num, limit_num, user_id=None):
        # return self.order_collection.find({USER_ID: ObjectId(user_id)}, {
        #     USER_ID: 0
        # }).skip(skip_num).limit(limit_num)
        return self.order_collection.aggregate([
            {
                "$unwind": "$good_ids"

            },
            {
                "$match":
                    {"user_id": ObjectId(user_id)}
            },
            {
                "$lookup": {
                    "from": "good",
                    "localField": "good_ids",
                    "foreignField": "_id",
                    "as": "order_good"
                }
            },
            {
                "$unwind": "$order_good"
            },
            {
                "$group":
                    {
                        "_id": {"order_id": "$_id", "bill_id": "$bill_id", "created_when": "$created_when"},
                        "total": {"$sum": "$order_good.price"}
                    }
            },
            {
                "$lookup": {
                    "from": "billing",
                    "localField": "_id.bill_id",
                    "foreignField": "_id",
                    "as": "billing_info"
                }
            },
            {
                "$project":
                    {
                        "order_id": "$_id.order_id",
                        "created_when": "$_id.created_when",
                        "billing_info.city": 1,
                        "billing_info.address": 1,
                        "billing_info.zip": 1,
                        "total": "$_id.total",
                        "total": 1,
                        "_id": 0
                        # "address": {"$concat":["$billing_info.city", "$billing_info.address", "$billing_info.zip"]}
                    }
            }
            # {
            #     "$skip": skip_num
            # },
            # {
            #     "$limit": limit_num
            # }

        ])
