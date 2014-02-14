from flask import Blueprint
from flask_sockets import Sockets

sockets = Blueprint('sockets', __name__, template_folder='')

# will these be routes?  web sockets work over ws:// URIs, 
@sockets.route('/send')


@sockets.route('/receive')
def echo_socket(ws):
    while True:
        message = ws.receive()
        ws.send(message)