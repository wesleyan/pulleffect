from flask import Blueprint
from flask import jsonify
from flask import json
from flask import request
from pulleffect.lib.utilities import mongo_connection
import pymongo


#create Blueprint
messages = Blueprint('messages', __name__, template_folder='templates')

# Get messages mongo collection
messages_collection = mongo_connection.messages

def get_messages():
    """Gets the all recent messages from database

    Keyword arguments:
    N/A

    Example route: 'http://localhost:3000/messages
    """
    ret = []
         
    for message in messages_collection.find(sort=[("time", pymongo.DESCENDING)]):
        message['_id'] = str(message['_id'])
        ret.append(message)
        return json.dumps(ret)
def post_messages(message):
    """Gets the most recent messages from database

    Keyword arguments:
    message-- new message

    Example route: 'http://localhost:3000/messages
    """


    fields = ['device', 'device_type', 'location', 'severity', 'description', 'time'];
    newMessage = {}
    errString = ""
    for f in fields:
        if (message.get(f, None) == None):
            errString += "Message is missing " + f + " field. " 
        else: 
            newMessage[f] = message.get(f)
    
    if errString:
        return make_response(jsonify({ 'error': err_string }), 404)
        
    newId = messages_collection.insert(newMessage)

    return jsonify({ 'id': str(newId) })
# Process message from device (ie cmdr), or return messages in queue

@messages.route('', methods=['GET', 'POST'])
def index():

    if request.method == 'GET': # return all messages
        get_messages()
    message = request.get_json()
    post_messages(message)



@messages.route('/<int:n>', methods=['GET'])
def get_messages(n):
    """Gets the n most recent messages from database

    Keyword arguments:
    n -- number of messages

    Example route: 'http://localhost:3000/messages/n'
    """

    ret = []
    for message in messages_collection.find(sort=[("time", pymongo.DESCENDING)],limit=n):
        message['_id'] = str(message['_id'])
        ret.append(message)
    return json.dumps(ret)