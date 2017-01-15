class Billing:
    def __init__(self, address, city, zip, phone):
        self.address = address
        self.city = city
        self.zip = zip
        self.phone = phone

    def getAddress(self):
        return self.address

    def getCity(self):
        return self.city

    def getZip(self):
        return self.zip

    def getPhone(self):
        return self.phone