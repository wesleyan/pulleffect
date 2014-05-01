from flask import Blueprint
from flask import jsonify
from flask import json
from flask import request
from flask import make_response
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


def add_notes(notes):
    """Adds notes to database

    Keyword arguments:
    notes -- the notes to add to the database

    Example route: 'http://localhost:3000/notes'
    """

    # Check notes exist
    if len(notes) == 0:
        return make_response(jsonify({'error': 'No notes submitted.'}), 404)

    # Note fields that must be submitted in POST request
    required_fields = ['text', 'author', 'time']

    # Init some parameters
    new_notes = []
    error_response = {}

    # Check all notes have all required fields
    for i in range(len(notes)):
        new_note = {}
        error_message = ""

        for field in required_fields:
            # If field is missing, add it to error message
            if (notes[i].get(field, None) is None):
                error_message += "{0}, ".format(field)
            else:
                new_note[field] = notes.get(field)
            # If error message, then append to error response
            if error_message:
                err = "Note is missing these fields: {0}"
                clean_error_message = err.format(error_message)[:-2]
                error_response[i] = clean_error_message
            new_notes.append(new_note)

    # If notes have any errors, return 404 NOT FOUND with
    # errors keyed by note index
    if len(error_response) > 0:
        return make_response(jsonify({'error': error_message}), 404)

    # Insert new notes into collection
    new_ids = notes_collection.insert(new_notes, {'ordered': True})

    # Return note ids?
    return jsonify({'id': str(new_ids)})


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
        get_notes(limit)
    # If POST request, add notes
    elif request.method == 'POST':
        # Get notes from request body and add them
        notes = request.get_json()
        add_notes(notes)
    # Otherwise throw 404 NOT FOUND
    return make_response(jsonify({'error': 'NOT FOUND'}), 404)
