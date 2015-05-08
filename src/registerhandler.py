__author__ = 'alay'


from .basehandler import BaseHandler
from couch import AsyncCouch
from tornado.gen import coroutine
import json


class RegisterHandler(BaseHandler):

    @coroutine
    def post(self, *args, **kwargs):
        data = json.loads(self.request.body.decode('utf-8'))
        client = AsyncCouch('radstat_users', BaseHandler.db_url)
        query = "function(doc){if(doc.username == '" + data['username'] + "' ){emit(doc, null)}} "
        view_doc = dict()
        view_doc['map'] = query
        view_doc['reduce'] = None
        result = yield client.temp_view(view_doc)
        if result['total_rows'] == 0:
            client.save_doc(data)
            client = AsyncCouch('logged_in_users', BaseHandler.db_url)
            new_doc = dict()
            print(data)
            new_doc['token'], new_doc['expiry'] = BaseHandler.get_token(data)
            new_doc['username'] = data['username']
            client.save_doc(new_doc)
            self.response = new_doc
            self.send_error(200)
        else:
            self.response['error'] = 'Username Taken'
            self.send_error(400)