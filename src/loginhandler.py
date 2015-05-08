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
        client = AsyncCouch('radstat_users', BaseHandler.db_url)
        query = "function(doc){if(doc.username == '" + data['username'] + "' " \
                "&& doc.password == '" + data['password'] + "'){emit(doc, null)}}"
        view_doc = dict()
        view_doc['map'] = query
        view_doc['reduce'] = None
        doc = yield client.temp_view(view_doc)
        if doc['total_rows'] == 0:
            self.response['error'] = "Wrong Username/Password Combination"
            self.send_error(403)
        else:
            client = AsyncCouch('logged_in_users', BaseHandler.db_url)
            new_doc = dict()
            new_doc['token'], new_doc['expiry'] = BaseHandler.get_token(data)
            new_doc['username'] = data['username']
            client.save_doc(new_doc)
            self.response = new_doc
            self.send_error(200)