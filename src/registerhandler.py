__author__ = 'alay'


from .basehandler import BaseHandler
from couch import AsyncCouch
from tornado.gen import coroutine
import json


class RegisterHandler(BaseHandler):

    @coroutine
    def post(self, *args, **kwargs):
        data = json.loads(self.request.body.decode('utf-8'))

        try:
            username = data['username']
        except Exception:
            self.send_error(400)

        input_query = {'username': username}
        flag = yield self.exists('radstat_users', input_query)
        if flag is True:
            self.response['error'] = 'Username Taken'
            self.send_error(400)
        else:
            self.set_db_client('radstat_users')
            yield self.db_client.save_doc(data)
            self.db_client.close()
            self.set_db_client('logged_in_users')
            new_doc = dict()
            new_doc['token'], new_doc['expiry'] = BaseHandler.get_token(data)
            new_doc['username'] = data['username']
            yield self.db_client.save_doc(new_doc)
            self.db_client.close()
            self.response = new_doc
            self.send_error(200)