from Models import User
from Properties import *
import pymongo
from pymongo import ReturnDocument
from Models import User


class UserController:
    def __init__(self, db):
        # type: (db) -> pymongo.database.Database
        self.user_collection = db['user']

    def addUser(self, user):
        return self.user_collection.insert_one({NAME: user.name, PASSWORD: user.password}).inserted_id

    def getUser(self, username):
        result = self.user_collection.find_one({NAME: username})
        if result is None:
            return None
        else:
            return User(name=result.get('username'), password=result.get('password'))

    def addTokens(self, user):
        return self.user_collection.find_one_and_update({NAME: user.name},
                                                        {"$set": {CODE: user.code,
                                                                  ACCESS_TOKEN: user.access_token,
                                                                  REFRESH_TOKEN: user.refresh_token,
                                                                  EXPIRATION_DATE: user.expiration_date,
                                                                  EXPIRES: user.expires}
                                                         }, {ID: 0,
                                                             CODE: 0,
                                                             NAME: 0,
                                                             PASSWORD: 0,
                                                             EXPIRATION_DATE: 0},
                                                        upsert=True, return_document=ReturnDocument.AFTER)

    def addCode(self, user):
        return self.user_collection.find_one_and_update({NAME: user.name},
                                                        {"$set": {CODE: user.code}
                                                         }, upsert=True)

    def get_user_by_code(self, code):
        return self.user_collection.find_one({CODE: code}, {ID: 0})

    def get_user_by_refresh_token(self, refresh_token):
        return self.user_collection.find_one({REFRESH_TOKEN: refresh_token}, {ID: 0})

    def verify_access_token(self, token):
        return self.user_collection.count({ACCESS_TOKEN: token})

    def get_user_info(self, token):
        return self.user_collection.find_one({ACCESS_TOKEN: token})

    def get_user_grant(self, token):
            return self.user_collection.find_one({ACCESS_TOKEN: token}, {
                PASSWORD: 0,
                ACCESS_TOKEN: 0,
                CODE: 0})
