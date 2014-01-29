from apiclient.discovery import build
from flask import Blueprint
from flask import jsonify
from flask import redirect
from flask import request
from flask import session
from flask import url_for
import httplib2
from oauth2client.client import flow_from_clientsecrets
from pulleffect.lib.utilities import mongo_connection
from pulleffect.lib.utilities import signin_required
import strict_rfc3339 
import requests
from urllib import urlencode

gcal = Blueprint('gcal', __name__, template_folder='templates')


# Build Google Calendar url
flow = flow_from_clientsecrets('./pulleffect/config/google_client_secrets.json',
                               scope='https://www.googleapis.com/auth/calendar',
                               redirect_uri='http://localhost:5000/gcal/authenticate')
auth_uri = flow.step1_get_authorize_url()

# Get users mongo collection
users = mongo_connection.users

# Get access token for Google Calendar
@gcal.route('/authenticate')
# @signin_required
def authenticate():
    # Exchange code if exists
    if (request.args.get('code')):
        credentials = flow.step2_exchange(request.args.get('code'))
        session['gcal_access_token'] = credentials.access_token
        return redirect(url_for('index'))

    # Handle error if exists
    if (request.args.get('error')):
        flash('Google authentication failed!\nError:' + str(request.args.get('error')), 'error')
        session['gcal_access_token'] = None
        return redirect(url_for('index'))
    print str(auth_uri)
    return redirect(auth_uri)


# Get Google Calendar list
@gcal.route('/get_calendar_list')
@signin_required
def get_calendar_list():
    # Get google id for user
    google_id = session.get('google_id')

    # Fetch user's calendars by google_id
    calendars = users.find_one({"google_id": google_id}, {"calendars":1, "_id":0})

    # Query Google for calendars if no calendars in mongo db
    if not calendars:
        return refresh_calendar_list()

    # Return user's calendars
    return jsonify({'calendars':calendars})

# Refresh Google Calendar list
@gcal.route('/refresh_calendar_list')
@signin_required
def refresh_calendar_list():
    gcal_access_token = session.get('gcal_access_token')      

    # Get calendar list
    req = requests.get('https://www.googleapis.com/calendar/v3/users/me/calendarList?' + urlencode({"access_token": gcal_access_token}))
    req = req.json()

    # Initialize return variables
    error = False
    calendar_list = []

    print req

    # Get error and calendar list
    if (req.get('error')):
        error = True
    else:
        calendars = req.get('items')
        for calendar_item in calendars:
            calendar_list.append({'calendar_name':calendar_item.get('summary'), 
                'calendar_id':calendar_item.get('id'), 
                'selected':False})

    # Return Google calendar list and error
    return jsonify({'error':error, 'calendars':calendar_list})

# Get Google Calendar events
@gcal.route('/get_calendar_events')
@signin_required
def get_calendar_events():
    # Get calender id
    cal_id = request.args.get('cal_id')
    cal_name = request.args.get('cal_name')

    # Stupid hack to get url encoding
    cal_id = urlencode({'cal':cal_id})[4:];    

    # Get gcal access_token
    gcal_access_token = session.get('gcal_access_token')

    min_time = strict_rfc3339.now_to_rfc3339_localoffset()

    req = requests.get('https://www.googleapis.com/calendar/v3/calendars/' + cal_id + '/events?' + urlencode({'access_token':gcal_access_token, 'maxResults': 5, 'orderBy': 'startTime', 'singleEvents':True, 'timeMin': min_time, 'fields': 'items(end,start,summary,description),summary'})  )
    # print events
    return jsonify({'calendar_events':req.json()})