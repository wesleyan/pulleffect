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

# Create blueprint
notes = Blueprint('notes', __name__, template_folder='templates')

# Get mongo connection to note collection
notes_collection = mongo_connection.notes


@notes.route('', methods=['GET', 'POST'])
def index():
    """Route controller for notes.

    Example route: 'http://localhost:3000/notes'
    """

    # If GET request, get notes
    if request.method == 'GET':
        # Get absolute value of the limit query value from query string
        limit = abs(int(request.args.get('limit', 10)))
        return get_notes(limit)

    # If POST request, add note
    elif request.method == 'POST':
        # Get note from request body and add to database
        return post_note(request.get_json())

    # Otherwise throw 404 NOT FOUND
    return make_response(jsonify({'error': 'NOT FOUND'}), 404)


def get_notes(limit):
    """Gets the most recent notes from database.

    Keyword arguments:
    limit -- max number of notes to retrieve (0 is infinite)

    Example route: 'http://localhost:3000/notes?limit=5'
    """
    ret = []
    sort_params = [("time", pymongo.DESCENDING)]

    # Get all notes
    for note in notes_collection.find(sort=sort_params, limit=limit):
        note['_id'] = str(note.get('_id'))
        ret.append(note)

    # Return jsonified array of notes
    return json.dumps(ret)


def post_note(note=None):
    """Inserts new note into database

    Keyword arguments:
    note -- new note

    Example route: 'http://localhost:3000/notes'
    """
    # Check note exists
    if note is None:
        return make_response(jsonify({'error': 'No note submitted.'}), 404)

    # Init default note
    new_note = {}

    # Required note fields
    required_fields = ['text', 'author']

    # Check note has required fields
    error = ""
    for field in required_fields:
        # If required field is missing, add to error
        if (note.get(field, None) is None):
            error += "{0}, ".format(field)
        else:
            new_note[field] = note.get(field)

    # If error exists, then return error response
    if error:
        info = "Submitted note is missing required fields: {0}"
        error += info.format(error)[:-2]
        return make_response(jsonify({'error': error}), 404)

    # Add current timestamp to note
    new_note["time"] = note.get("time", datetime.now())

    # Insert new note into collection
    newId = notes_collection.insert(new_note)

    # Return id of newly submitted note
    return jsonify({'id': str(newId)})
