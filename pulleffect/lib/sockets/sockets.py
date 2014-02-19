import 
from flask import Blueprint
from flask_sockets import Sockets

sockets = Blueprint('sockets', __name__, template_folder='')

class ChatBackend(object):
	"""
	"""

	def __init__(self):
		self.clients = list()
		# self.pubsub.subscribe() WHAT WHY
		# ...

	def __iterdata(self):

	def register(self, client):


@app.route('/')
def hello():
    return render_template('index.html')

@sockets.route('/submit')
def inbox(ws):
    """Receives incoming chat messages, inserts them into Redis."""
    while ws.socket is not None:
        # Sleep to prevent *contstant* context-switches.
        gevent.sleep(0.1)
        message = ws.receive()

        if message:
            app.logger.info(u'Inserting message: {}'.format(message))
            redis.publish(REDIS_CHAN, message)

@sockets.route('/receive')
def outbox(ws):
    """Sends outgoing chat messages, via `ChatBackend`."""
    chats.register(ws)

    while ws.socket is not None:
        # Context switch while `ChatBackend.start` is running in the background.
        gevent.sleep()