from Models import Billing
from Properties import *
import pymongo
from bson.objectid import ObjectId


class BillingController:
    def __init__(self, db):
        # type: (db) -> pymongo.database.Database
        self.bill_collection = db['billing']


    def createBilling(self, billing):
        return self.bill_collection.insert({ADDRESS: billing.getAddress(),
                                            CITY: billing.getCity(),
                                            ZIP: billing.getZip(),
                                            PHONE: billing.getPhone()})

    def getBilling(self, bill_id):
        return self.bill_collection.find_one({ID : bill_id})

    def getBillingByObject(self, bill_id):
        return self.bill_collection.find_one({ID : ObjectId(bill_id)})