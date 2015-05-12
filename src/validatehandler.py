__author__ = 'alay'


from .basehandler import BaseHandler
from couch import AsyncCouch
from tornado.gen import coroutine
import json


class ValidateHandler(BaseHandler):

    @coroutine
    def post(self, *args, **kwargs):

        try:
            token = self.get_argument('token')
            module = self.get_argument('moduleName')
        except Exception:
            self.send_error(400)

        flag, doc = yield self.validate(token)

        if flag is True:
            self.send_error(200)
        else:
            self.response['error'] = "Token Doesnt Exist"
            self.send_error(403)