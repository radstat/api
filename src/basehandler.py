__author__ = 'alay'

from tornado.web import RequestHandler
from os.path import dirname
import traceback
import json
import datetime
import hashlib


class BaseHandler(RequestHandler):

    root = dirname(__file__).rstrip('/src')
    db_url = "http://admin:admin@localhost:5984"

    @staticmethod
    def get_token(data):
        username = data['username']
        password = data['password']
        time = datetime.datetime.timestamp(datetime.datetime.now())
        expiry_time = time + float(3600)
        data = (username + password + str(expiry_time)).encode('utf-8')
        token = hashlib.md5(data)
        return token.hexdigest(), str(expiry_time)


    def initialize(self):
        # you can connect to a db and store it in self.client
        # self.client = redis.StrictRedis()

        # you can store the response in self.response
        self.response = {}
        # 1 week of expiry time configured here
        self.expiry = float(3600)
        # dbhost configures here
        self.dbhost = 'http://admin:admin@localhost:5984'

    def options(self, *args, **kwargs):
        self.send_error(200)

    def write_error(self, status_code, **kwargs):
        if self.settings.get("serve_traceback") and "exc_info" in kwargs:
            # in debug mode, try to send a traceback
            self.set_header('Content-Type', 'application/json')
            for line in traceback.format_exception(*kwargs["exc_info"]):
                self.write(line)
            self.finish()
        else:
            if (list(self.response.keys()).__len__()) == 0:
                self.response['status'] = status_code
                self.response['message'] = self._reason

            # This is a set of headers for CORS

            self.set_header('Content-Type', 'application/json')
            self.set_header("Access-Control-Allow-Origin", "*")
            self.set_header("Access-Control-Allow-Credentials", "false")
            self.set_header("Access-Control-Expose-Headers", "*")
            self.set_header("Access-Control-Allow-Methods", "Post, Options")
            self.set_header("Access-Control-Allow-Headers", "Accept, Content-Type")
            self.finish(json.dumps(self.response))
