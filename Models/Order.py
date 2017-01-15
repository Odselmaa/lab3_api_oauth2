import time


class Order:
    def __init__(self, order_id, user_id, good_ids=[], bill_id=None, created_date=int(round(time.time() * 1000))):
        self.user_id = user_id
        self.good_ids = good_ids
        self.bill_id = bill_id
        self.order_id = order_id
        self.created_when = created_date

    def get_user_id(self):
        return self.user_id

    def get_product_id(self):
        return self.good_ids

    def get_bill_id(self):
        return self.bill_id

    def get_id(self):
        return self.order_id

    def get_created_when(self):
        return self.created_when