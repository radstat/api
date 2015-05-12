__author__ = 'alay'

from tornado.web import RequestHandler
from tornado.gen import coroutine
from couch import AsyncCouch
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
        return token.hexdigest(), expiry_time

    @staticmethod
    def get_query(input_dict):
        query = "function(doc){if("
        condition = ""
        for key in input_dict:
            condition += "doc." + key + " == '" + input_dict[key] + "' && "
        condition = condition[0:-4]
        query += condition + "){emit(doc, null)}}"
        return query

    def initialize(self):
        # you can connect to a db and store it in self.client
        # self.client = redis.StrictRedis()

        # you can store the response in self.response
        self.response = {}
        # 1 week of expiry time configured here
        self.expiry = float(3600)
        # dbhost configures here
        self.dbhost = 'http://admin:admin@localhost:5984'

        self.db_client = None

        self.db_doc = None

    def set_db_client(self, db_name):
        self.db_client = AsyncCouch(db_name, self.db_url)

    @coroutine
    def exists(self, db_name, input_dict):
        self.set_db_client(db_name)
        query = BaseHandler.get_query(input_dict)
        view_doc = dict()
        view_doc['map'] = query
        view_doc['reduce'] = None
        self.db_doc = yield self.db_client.temp_view(view_doc)
        self.db_client.close()
        if self.db_doc is not None:
            if self.db_doc['total_rows'] == 1:
                return True
            else:
                return False
        else:
            return False

    @coroutine
    def validate(self, token):
        query_input = {'token': token}
        if(yield self.exists('logged_in_users', query_input)) is True:
            doc = self.db_doc['rows'][0]['key']
            # print(doc)
            # print(self.db_doc)
            expiry_time = float(self.db_doc['rows'][0]['key']['expiry'])
            current_time = datetime.datetime.timestamp(datetime.datetime.now())
            self.set_db_client('logged_in_users')
            if current_time >= expiry_time:
                yield self.db_client.delete_doc(doc)
                self.db_client.close()
                return False, None
            else:
                doc['expiry'] = current_time + float(3600)
                yield self.db_client.save_doc(doc)
                self.db_client.close()
                return True, doc
        else:
            return False, None

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
