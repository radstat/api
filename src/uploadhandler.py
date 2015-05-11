__author__ = 'alay'

from .basehandler import BaseHandler
from couch import AsyncCouch
from tornado.gen import coroutine
import os
import json
import zipfile


class UploadHandler(BaseHandler):

    @coroutine
    def post(self, *args, **kwargs):

        print(self.request.body)
        data = json.loads(self.request.body.decode('utf-8'))
        token = data['token']
        module = data['moduleName']
        token = "288412e0d8bbbe7a471116370590c520"
        module = "template"
        client = AsyncCouch('logged_in_users', BaseHandler.db_url)
        query = "function(doc){if(doc.token == '" + token + "'){emit(doc, null)}}"
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
            username = result['rows'][0]['key']['username']

            file = self.request.files['file'][0]
            file_name = file['filename']
            user_path = BaseHandler.root.rstrip('/api') + '/static-server/static/' + username
            file_path = user_path + '/' + module
            zip_file_path = file_path + '.zip'
            if not os.path.isdir(user_path):
                os.mkdir(user_path)

            if os.path.isdir(file_path):
                print('exits')
                remove_command = 'rm -rf ' + file_path
                os.system(remove_command)

            with open(zip_file_path, 'wb') as temp_file:
                temp_file.write(file['body'])
            zip_extractor = zipfile.ZipFile(zip_file_path)
            extract_path = file_path.rstrip(file_name)
            zip_extractor.extractall(extract_path)
            os.unlink(zip_file_path)
            self.send_error(200)