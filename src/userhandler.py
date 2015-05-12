__author__ = 'alay'


from .basehandler import BaseHandler
from couch import AsyncCouch
from tornado.gen import coroutine
import json


class UserHandler(BaseHandler):

    @coroutine
    def post(self, *args, **kwargs):
        data = json.loads(self.request.body.decode('utf-8'))

        try:
            token = data['token']
        except Exception:
            self.send_error(400)

        flag, doc = yield self.validate(token)
        if flag is True:
            username = doc['username']
            input_query = {'username': username}
            flag = yield self.exists('radstat_users', input_query)
            if flag is True:
                self.response = self.doc
                del self.response['_rev']
                del self.response['_id']
                self.send_error(200)
            else:
                self.send_error(400)
        else:
            self.response['error'] = 'token'
            self.send_error(400)