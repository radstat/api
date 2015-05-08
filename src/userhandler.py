__author__ = 'alay'


from .basehandler import BaseHandler
from couch import AsyncCouch
from tornado.gen import coroutine
import json


class UserHandler(BaseHandler):

    @coroutine
    def post(self, *args, **kwargs):
        data = json.loads(self.request.body.decode('utf-8'))
        client = AsyncCouch('logged_in_users', BaseHandler.db_url)
        query = "function(doc){if(doc.token == '" + data['token'] + "'){emit(doc, null)}}"
        view_doc = dict()
        view_doc['map'] = query
        view_doc['reduce'] = None
        doc = yield client.temp_view(view_doc)
        if doc['total_rows'] == 0:
            self.response['error'] = "Token Doesnt Exist"
            self.send_error(403)
        else:
            client = AsyncCouch('radstat_users', BaseHandler.db_url)
            username = doc['rows'][0]['key']['username']
            query = "function(doc){if(doc.username == '" + username + "' ){emit(doc, null)}} "
            view_doc = dict()
            view_doc['map'] = query
            view_doc['reduce'] = None
            result = yield client.temp_view(view_doc)
            del result['rows'][0]['key']['_rev']
            del result['rows'][0]['key']['_id']
            self.response = result['rows'][0]['key']
            self.send_error(200)