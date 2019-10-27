import hashlib
from model import Client


class Auth:
    login = ''
    password = ''

    def login(self, login, password):
        user = Client.query.filter_by(client_login=login, password=password).first()

        if user:
            return True
        else:
            return False

    def isLoggedUser(self, cookies):
        if not cookies.get('userID') or not cookies.get('client_login'):
            return False

        client = Client.query.filter_by(client_login=cookies.get('client_login')).first()
        if not client:
            return False

        h = hashlib.sha1(str.encode(client.password))
        p = h.hexdigest()
        return p == cookies.get('userID')

    def validate(self, post):
        errors = False
        if post.get('password') != post.get('password_confirm') or len(post.get('login')) < 3:
            errors = True

        return not errors 

