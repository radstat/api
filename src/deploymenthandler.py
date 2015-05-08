__author__ = 'alay'

from .basehandler import BaseHandler
import os


class DeploymentHandler(BaseHandler):

    def post(self, *args, **kwargs):
        print(self.request)
        file = self.request.files['file'][0]
        file_name = file['filename']
        path = BaseHandler.root + '/static/' + file_name.rstrip('.zip')
        if os.path.isdir(path):
            print('exits')
            remove_command = 'rm -rf ' + BaseHandler.root + '/static/' + file['filename'].rstrip('.zip')
            os.system(remove_command)
        command = 'unzip ' + file['filename'] + ' -d ' + path
        with open(file_name, 'wb') as temp_file:
            temp_file.write(file['body'])
        print(command)
        os.system(command)
        os.unlink(file_name)
        self.redirect(self.request.headers['Referer'])