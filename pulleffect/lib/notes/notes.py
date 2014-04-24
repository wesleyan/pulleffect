from flask import Blueprint
from flask import jsonify
from flask import json
from flask import request
from flask import make_response
from pulleffect.lib.utilities import mongo_connection
import pymongo

notes = Blueprint('notes', __name__, template_folder='templates')

# Get notes mongo collection
notes_collection = mongo_connection.notes

# Respond with most recent notes
# Can take a query string like this: 'http://localhost:3000/notes?limit=5'
@notes.route('', methods=['GET', 'POST'])
def index():
	if request.method == 'GET': # return all messages

		# Gets the limit query parameter from the url
		# Sets the limit to 0 if the query parameter does not exist
		# In mongo, limit(0) is the same as setting no limit 
		limit = request.args.get('limit', 0)

		ret = []
		for note in notes_collection.find(sort=[("time", pymongo.DESCENDING)]).limit(limit):
			if (note != None) and (note.get('_id') != None):
				note['_id'] = str(note.get('_id'))
				ret.append(note)

		# Since REST APIs are meant to respect idempotence, return a 404
		# when there are no routes in the db
		if len(ret) == 0:
			return make_response(jsonify({ 'error': 'No notes found.' }), 404)

		return json.dumps(ret)

	# Add new note
	note = request.get_json()

	if (note == None):
		return make_response(jsonify({ 'error': 'No note submitted.' }), 404)

	required_fields = ['text', 'author', 'time']
	new_note = {}
	err_string = ""

	for field in required_fields:
		if (note.get(field, None) == None):
			err_string += "Note is missing " + field + " field. "
		else:
			new_note[field] = note.get(field)

	if err_string:
		return make_response(jsonify({ 'error': err_string }), 404)

	new_id = notes_collection.insert(new_note)
	return jsonify({ 'id' : str(new_id) })
