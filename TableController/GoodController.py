from Properties import *
class GoodController:
    def __init__(self, db):
        self.db = db

    def getGoodAll(self, skipNum, limitNum):
        return self.db.good.find().skip(skipNum).limit(limitNum)


    def getGood(self, id):
        return self.db.good.find({"_id":id})

    def getGoodByIds(self, ids):
        return self.db.good.find({"_id": {"$in": ids}}, {ID: 0, DESC: 0})

    def getSize(self):
        return self.db.good.count()