from apiclient.discovery import build
from flask import Blueprint
from flask import jsonify
from flask import json
from flask import redirect
from flask import request
from flask import session
from flask import url_for
from oauth2client.client import flow_from_clientsecrets
from pulleffect.lib.utilities import mongo_connection
from urllib import urlencode
import strict_rfc3339 
import requests
import httplib2
import pymongo

messages = Blueprint('messages', __name__, template_folder='templates')

# Get users mongo collection
messages_collection = mongo_connection.messages

# Process message from device (ie cmdr), or return messages in queue
@messages.route('', methods=['GET', 'POST'])
def index():
    if request.method == 'GET': # return all messages
        ret = []
        for message in messages_collection.find(sort=[("time", pymongo.DESCENDING)]):
            message['_id'] = str(message['_id'])
            ret.append(message)
        return json.dumps(ret)
    # we are adding a new message
    message = request.get_json()
    newId = messages_collection.insert({
        'device':message.get('device', None), 'device_type':message.get('device_type', None),
        'location':message.get('location', None), 'severity':message.get('severity', None),
        'description':message.get('description', None), 'time':message.get('time', None)
        })
    return jsonify({ 'id': str(newId) })


@messages.route('/<int:n>', methods=['GET'])
def get_messages(n):
    ret = []
    for message in messages_collection.find(sort=[("time", pymongo.DESCENDING)],limit=n):
        message['_id'] = str(message['_id'])
        ret.append(message)
    return json.dumps(ret)