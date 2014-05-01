from flask import Blueprint
from flask import jsonify
from flask import json
from flask import request
from pulleffect.lib.utilities import mongo_connection
import pymongo

messages = Blueprint('messages', __name__, template_folder='templates')

# Get messages mongo collection
messages_collection = mongo_connection.messages
sort_params = [("time", pymongo.DESCENDING)]


# Process message from device (ie cmdr), or return messages in queue
@messages.route('', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':  # return all messages
        ret = []
        for message in messages_collection.find(sort=sort_params):
            message['_id'] = str(message['_id'])
            ret.append(message)
        return json.dumps(ret)
    # we are adding a new message
    message = request.get_json()

    fields = ['device', 'device_type',
              'location', 'severity',
              'description', 'time']
    newMessage = {}
    errString = ""
    for f in fields:
        if (message.get(f, None) is None):
            errString += "Message is missing " + f + " field. "
        else:
            newMessage[f] = message.get(f)
    if errString:
        return jsonify({'error': errString})

    newId = messages_collection.insert(newMessage)
    return jsonify({'id': str(newId)})


@messages.route('/<int:n>', methods=['GET'])
def get_messages(n):
    ret = []
    for message in messages_collection.find(sort=sort_params, limit=n):
        message['_id'] = str(message['_id'])
        ret.append(message)
    return json.dumps(ret)
