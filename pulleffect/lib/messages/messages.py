# Copyright (C) 2014 Wesleyan University
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from flask import Blueprint
from flask import jsonify
from flask import json
from flask import request
from flask import make_response
from datetime import datetime
from pulleffect.lib.utilities import mongo_connection
import pymongo


#create Blueprint
messages = Blueprint('messages', __name__, template_folder='templates')

# Get messages mongo collection
messages_collection = mongo_connection.messages
sort_params = [("time", pymongo.DESCENDING)]


# Process message from device (ie cmdr), or return messages in queue
def post_messages(message):
    """Gets the most recent messages from database

    Keyword arguments:
    message-- new message

    Example route: 'http://localhost:3000/messages
    """
    fields = ['device', 'device_type',
              'location', 'severity',
              'description']
    newMessage = {}
    errString = ""
    for f in fields:
        if (message.get(f, None) is None):
            errString += "Message is missing {0} field.".format(f)
        else:
            newMessage[f] = message.get(f)

    if errString:
        return make_response(jsonify({'error': errString}), 404)

    # Give current timestamp
    newMessage["time"] = newMessage.get("time", datetime.now())
    newId = messages_collection.insert(newMessage)

    return jsonify({'id': str(newId)})


@messages.route('', methods=['GET', 'POST'])
def index():
    """Takes care of GET and POST requests at /messages url

    Keyword arguments:
    N/A

    Example route: 'http://localhost:3000/messages'
    """
    if request.method == 'GET':  # return all messages
        limit = abs(int(request.args.get('limit', 0)))
        return get_messages(limit)
    message = request.get_json()
    return post_messages(message)


def get_messages(limit=0):
    """Gets the all recent messages from database

    Keyword arguments:
    N/A

    Example route: 'http://localhost:3000/messages
    """
    ret = []
    for message in messages_collection.find(sort=sort_params, limit=limit):
        message['_id'] = str(message['_id'])
        ret.append(message)
    return json.dumps(ret)
