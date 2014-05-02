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


def get_notes(integer_limit):
    """Gets the most recent notes from database

    Keyword arguments:
    integer_limit -- the limit on notes returned

    Example route: 'http://localhost:3000/notes?limit=5'
    """
    ret = []
    # Check all notes have valid id and append to return array
    sort_params = [("time", pymongo.DESCENDING)]
    for note in notes_collection.find(sort=sort_params).limit(integer_limit):
        if (note is not None) and (note.get('_id') is not None):
            note['_id'] = str(note.get('_id'))
            ret.append(note)

    # Return 404 NOT FOUND when no notes in database
    if len(ret) == 0:
        return make_response(jsonify({'error': 'No notes found.'}), 404)

    # Return jsonified array of notes
    return json.dumps(ret)


def add_note(note=None):
    """Adds notes to database

    Keyword arguments:
    notes -- the notes to add to the database

    Example route: 'http://localhost:3000/notes'
    """

    # Check notes exist
    if note is None:
        return make_response(jsonify({'error': 'No notes submitted.'}), 404)

    # Note fields that must be submitted in POST request
    required_fields = ['text', 'author']

    # Init some parameters
    error_response = {}
    newNote = {}
    # Check all notes have all required fields
    clean_error_message = ""
    error_message = ""
    for field in required_fields:
        # If field is missing, add it to error message
        if (note.get(field, None) is None):
            error_message += "{0}, ".format(field)
        else:
            newNote[field] = note.get(field)
        # If error message, then append to error response
        if error_message:
            err = "Note is missing these fields: {0}"
            clean_error_message += err.format(error_message)[:-2]

    newNote["time"] = note.get("time", datetime.now())
    # If notes have any errors, return 404 NOT FOUND with
    # errors keyed by note index
    if len(error_response) > 0:
        return make_response(jsonify({'error': error_message}), 404)

    # Insert new notes into collection
    newId = notes_collection.insert(newNote)

     # Give current timestamp
    # Return note ids?
    return jsonify({'id': str(newId)})


@notes.route('', methods=['GET', 'POST'])
def index():
    """Route controller for notes

    Keyword arguments:
    route_url -- the url where this route can be found on the server
    methods -- accepted request types
    """

    # If GET request, get notes
    if request.method == 'GET':
        # Get absolute value of the limit query value from query string
        limit = abs(int(request.args.get('limit', 0)))
        # Get notes with limit
        return get_notes(limit)
    # If POST request, add notes
    elif request.method == 'POST':
        # Get notes from request body and add them
        note = request.get_json()
        return add_note(note)
    # Otherwise throw 404 NOT FOUND
    return make_response(jsonify({'error': 'NOT FOUND'}), 404)
