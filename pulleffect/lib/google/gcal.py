from apiclient.discovery import build
from flask import Blueprint
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
import httplib2
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import AccessTokenRefreshError
from oauth2client.file import Storage
from pulleffect.lib.utilities import mongo_connection
from pulleffect.lib.utilities import signin_required
import moment
from datetime import datetime
import requests

gcal = Blueprint('gcal', __name__, template_folder='templates')


# Build Google Calendar url
flow = flow_from_clientsecrets('./pulleffect/config/google_client_secrets.json',
                               scope='https://www.googleapis.com/auth/calendar',
                               redirect_uri='http://localhost:5000/gcal/authenticate')
auth_uri = flow.step1_get_authorize_url()
storage = Storage('./pulleffect/config/credentials_file')


# Get access token for Google Calendar
@gcal.route('/authenticate')
@signin_required
def authenticate():
    if (request.args.get('code')):
        credentials = flow.step2_exchange(request.args.get('code'))
        session['gcal_access_token'] = credentials.access_token
        storage.put(credentials)
        return redirect(url_for('index'))
    if (request.args.get('error')):
        print request.args.get('error')
        session['gcal_access_token'] = None
        return redirect(url_for('index'))
    print auth_uri
    return redirect(auth_uri)


# Get Google Calendar list
@gcal.route('/get_calendar_list')
@signin_required
def get_calendar_list():
    # Get user
    users = mongo_connection.users
    user = users.find_one({"name":"Arthur"}, { "calendars": 1 });
    calendar_list = user.get('calendars')

    # Query Google for calendars if no calendars in mongo db
    if not calendar_list:
        return refresh_calendar_list()

    # Return user's calendars
    return jsonify({'calendars':calendar_list})


# Refresh Google Calendar list
@gcal.route('/refresh_calendar_list')
@signin_required
def refresh_calendar_list():
    # Get credentials
    credentials = storage.get()
    http = httplib2.Http()
    http = credentials.authorize(http)

    # Get Google calendar API
    service = build('calendar', 'v3', http=http)
    calendar_list = []
    page_token = None

    # Get Google calendar list
    while True:
        try:
            calendars = service.calendarList().list(pageToken=page_token).execute()
            for calendar in calendars['items']:
                calendar_list.append({'calendar_name':calendar['summary'], 'calendar_id':calendar['id'], 'selected':False})
            page_token = calendars.get('nextPageToken')
            if not page_token:
                break
        except AccessTokenRefreshError:
            session['gcal_access_token'] = None
            return jsonify({'error':'AccessTokenRefreshError'})

    # Update user in mongo db
    users = mongo_connection.users
    users.update({"name":"Arthur"}, {"$set": {"calendars":calendar_list}})

    # Return Google calendar list
    return jsonify({'calendars':calendar_list})

# Get Google Calendar events
@gcal.route('/get_calendar_events')
@signin_required
def get_calendar_events():

    credentials = storage.get()
    http = httplib2.Http()
    http = credentials.authorize(http)
    service = build('calendar', 'v3', http=http)

    page_token = None
    calID = 'wesleyan.edu_iq47a44fno2qb4jgio7plob91c@group.calendar.google.com'
    

    events = service.events().list(calendarId=calID, pageToken=page_token, orderBy="startTime", singleEvents=True).execute()
    return jsonify({'calendar_events':events})
    
