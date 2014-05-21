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

# Create Blueprint
messages = Blueprint('messages', __name__, template_folder='templates')

# Get mongo messages collection
messages_collection = mongo_connection.messages


@messages.route('', methods=['GET', 'POST'])
def index():
    """Route controller for messages.

    Example route: 'http://localhost:3000/messages'
    """
    # If GET request, get messages
    if request.method == 'GET':
        # Get absolute value of `limit` from query string
        limit = abs(int(request.args.get('limit', 10)))
        return get_messages(limit)

    # If POST request, add message
    elif request.method == 'POST':
        # Get message from request body and add to database
        return post_message(request.get_json())

    # Otherwise throw 404 NOT FOUND
    else:
        return make_response(jsonify({'error': 'NOT FOUND'}), 404)


def get_messages(limit):
    """Gets the all recent messages from database.

    Args:
    limit -- max number of messages to retrieve (0 is infinite)

    Example route: 'http://localhost:3000/messages
    """
    ret = []
    sort_params = [("time", pymongo.DESCENDING)]

    # Get all messages
    for message in messages_collection.find(sort=sort_params, limit=limit):
        message['_id'] = str(message['_id'])
        ret.append(message)

    # Return jsonified array of messages
    return json.dumps(ret)


def post_message(message):
    """Inserts new message in database.

    Args:
    message -- new message

    Example route: 'http://localhost:3000/messages
    """
    # Check message exists
    if message is None:
        return make_response(jsonify({'error': 'No message submitted.'}), 404)

    # Init default message
    new_message = {}

    # Required message fields
    required_fields = [
        'device', 'device_type', 'location', 'severity', 'description'
    ]

    # Check message has required fields
    error = ""
    for field in required_fields:
        # If message is missing required field, add to error
        if (message.get(field, None) is None):
            error += "{0}, ".format(field)
        else:
            new_message[field] = message.get(field)

    # If error exists, then return error response
    if error:
        info = "Submitted message is missing required fields: {0}"
        error = info.format(error)[:-2]
        return make_response(jsonify({'error': error}), 404)

    # Add current timestamp to message
    new_message["time"] = new_message.get("time", datetime.now())

    # Insert new message into collection
    newId = messages_collection.insert(new_message)

    # Return id of newly submitted message
    return jsonify({'id': str(newId)})
