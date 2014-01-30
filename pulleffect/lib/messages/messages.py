from apiclient.discovery import build
from flask import Blueprint, jsonify, redirect, request, session, url_for
import httplib2
from oauth2client.client import flow_from_clientsecrets
from pulleffect.lib.utilities import mongo_connection
import strict_rfc3339 
import requests
from urllib import urlencode

messages = Blueprint('messages', __name__, template_folder='templates')

# Get users mongo collection
messagesCollection = mongo_connection.messages

@messages.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET': # return all messages
        ret = []
        for message in messagesCollection.sort("date", 1):
            ret += message
        return jsonify(ret)
    # we are adding a new message
    newId = messagesCollection.insert({
        'device': request.form['device'], 'device_type': request.form['device_type'],
        'location': request.form['location'], 'severity': request.form['severity'],
        'title': request.form['title'], 'description': request.form['description'],
        'time': request.form['time']
    })
    return jsonify({ 'id': newId })
