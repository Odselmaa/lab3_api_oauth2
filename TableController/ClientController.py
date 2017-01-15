from Models import User
from Properties import *
import pymongo

class ClientController:
    def __init__(self, db):
        self.client_collection = db['client']


    def addClient(self, client):
        return self.client_collection.insert_one({APP_NAME:client.app_name,
                                           CLIENT_ID:client.client_id,
                                           CLIENT_SECRET:client.client_secret}).inserted_id

    def getClient(self, app_name):
        return self.client_collection.find_one({APP_NAME : app_name})


    def getClientById(self, client_id):
        return self.client_collection.find_one({CLIENT_ID : client_id})

