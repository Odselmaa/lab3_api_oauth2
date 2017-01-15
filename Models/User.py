class User:
    def __init__(self,
                 name,
                 password = None,
                 access_token=None,
                 refresh_token=None,
                 token_type=None,
                 code = None,
                 expires=None,
                 expiration_date = None):
        self.name = name
        self.password = password
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_type = token_type
        self.expires = expires
        self.expiration_date = expiration_date
        self.code = code
