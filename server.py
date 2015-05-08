__author__ = 'alay'


from tornado.httpserver import HTTPServer
from tornado.web import Application
from tornado.ioloop import IOLoop
from tornado.options import define, options
from src.deploymenthandler import DeploymentHandler
from src.registerhandler import RegisterHandler
from src.loginhandler import LoginHandler
from src.validatehandler import ValidateHandler
from src.userhandler import UserHandler


define('ip', default='0.0.0.0', type=str, help='Give the ip on which the server will bind')

app = Application([
    (r'/api/register', RegisterHandler),
    (r'/api/login', LoginHandler),
    (r'/api/validate', ValidateHandler),
    (r'/api/user', UserHandler),
    (r'/api/deployment', DeploymentHandler)
])

server = HTTPServer(app)
server.listen(8000, options.ip)
IOLoop.instance().start()