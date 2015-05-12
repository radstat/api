__author__ = 'alay'

from .basehandler import BaseHandler
from tornado.gen import coroutine
import os
import zipfile


class UploadHandler(BaseHandler):

    @coroutine
    def post(self, *args, **kwargs):

        try:
            token = self.get_argument('token')
            module = self.get_argument('moduleName')
        except Exception:
            self.send_error(400)

        flag, doc = yield self.validate(token)

        if flag is True:
            self.set_db_client('radstat_users')
            username = doc['username']
            file = self.request.files['file'][0]
            user_path = BaseHandler.root.rstrip('/api') + '/static-server/static/' + username
            file_path = user_path + '/' + module
            zip_file_path = file_path + '.zip'

            if not os.path.isdir(user_path):
                os.mkdir(user_path)

            if os.path.isdir(file_path):
                remove_command = 'rm -rf ' + file_path
                os.system(remove_command)

            with open(zip_file_path, 'wb') as temp_file:
                temp_file.write(file['body'])
            zip_extractor = zipfile.ZipFile(zip_file_path)
            zip_extractor.extractall(user_path + "/" + module)
            os.unlink(zip_file_path)
            self.send_error(200)
        else:
            self.response['error'] = "Token Doesnt Exist"
            self.send_error(403)