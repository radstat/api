__author__ = 'alay'


from .basehandler import BaseHandler
from couch import AsyncCouch
from tornado.gen import coroutine
import json
import datetime
import hashlib

class LoginHandler(BaseHandler):

    @coroutine
    def post(self, *args, **kwargs):
        data = json.loads(self.request.body.decode('utf-8'))
        method = None
        try:
            username = data['username']
            password = data['password']
            method = 'username'
        except Exception:
            try:
                token = data['token']
                method = 'token'
            except Exception:
                self.send_error(400)
        if method == 'username':
            query_input = {'username': username}
            flag = yield self.exists('radstat_users', query_input)
            if flag is True:
                if password == self.doc['password']:
                    self.set_db_client('logged_in_users')
                    new_doc = dict()
                    new_doc['token'], new_doc['expiry'] = BaseHandler.get_token(data)
                    new_doc['username'] = username
                    yield self.db_client.save_doc(new_doc)
                    self.response = new_doc
                    self.send_error(200)
                else:
                    self.response['error'] = "password"
                    self.send_error(403)
            else:
                self.response['error'] = 'username'
                self.send_error(403)
        elif method == 'token':
            flag, doc = yield self.validate(token)
            if flag is True:
                self.response = doc
                self.send_error(200)
            else:
                self.response['error'] = 'token'
                self.send_error(403)
