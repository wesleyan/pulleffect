
# Copyright (C) 2014 Wesleyan University#
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


import json

from apiclient.discovery import build_from_document
from flask import Blueprint
from flask import jsonify
from flask import redirect
from flask import request
from flask import session
from flask import url_for
import httplib2
from oauth2client.client import AccessTokenCredentials
from oauth2client.client import OAuth2WebServerFlow
from pulleffect.config.env import config
from pulleffect.lib.utilities import cache
from pulleffect.lib.utilities import mongo_connection
from pulleffect.lib.utilities import signin_required
import requests
import logging

gcal = Blueprint('gcal', __name__, template_folder='templates')

google_client_secrets = json.load(open(config["google_client_secrets"]))
google_client_secrets = google_client_secrets.get("web")

CLIENT_ID = google_client_secrets.get("client_id")
CLIENT_SECRET = google_client_secrets.get("client_secret")
GOOGLE_TOKEN_API = "https://accounts.google.com/o/oauth2/token"
GOOGLE_CALENDAR_API = "https://www.googleapis.com/auth/calendar"
GOOGLE_TOKEN_INFO_API = "https://www.googleapis.com/oauth2/v1/tokeninfo"
GCAL_DISCOVERY = json.load(open(config["gcal_discovery"]))
REDIRECT_URI = config['home_url'] + '/gcal/oauth2callback'
APPROVAL_PROMPT = 'force'

# Get users mongo collection
users = mongo_connection.users


@gcal.route('/authenticate')
@signin_required
def authenticate():
    """Route authenticates user with Google Calendar.
    """
    # Get google id for connected user
    google_id = session.get("google_id", None)

    # Get Google auth uri
    auth_uri = get_google_auth_uri_for_user(google_id)
    return redirect(auth_uri)


@gcal.route('/oauth2callback')
@signin_required
def oauth2callback():
    """Route controller completes Google Calendar authentication.
    """
    # Get code from query string
    code = request.args.get('code', None)

    if code:
        # Build OAuth2 web server flow from authorization code
        flow = OAuth2WebServerFlow(
            CLIENT_ID,
            CLIENT_SECRET,
            GOOGLE_CALENDAR_API)
        flow.redirect_uri = request.base_url

        # Get credentials from authorization code
        try:
            credentials = flow.step2_exchange(code)
        except Exception as e:
            error_message = "Unable to get a Google access token because {0}"
            logging.warning(error_message.format(e.message))

        # Get Google id for connected user
        google_id = session.get("google_id", None)

        # Get Google refresh token for connected user
        refresh_token = get_connected_user_refresh_token(google_id)

        # If refresh token is invalid, refresh it
        if refresh_token is None:
            refresh_token = credentials.refresh_token

        # Update connected user's refresh token
        users.update(
            {"google_id": google_id},
            {"$set": {
                "gcal_refresh_token": refresh_token,
                "gcal_user_agent": credentials.user_agent
            }},
            upsert=False)

        # Update Google credentials in session for connected user
        session["gcal_credentials"] = {
            "access_token": credentials.access_token,
            "user_agent": credentials.user_agent
        }

    # Redirect to the main page of the application
    return redirect(url_for('index'))


@gcal.route('/calendar_list')
@signin_required
def calendar_list():
    """Route controller fetches array of calendars from Google Calendar.
    """
    # Check the oauth creds and refresh if necessary
    credentials = try_get_oauth_creds()
    if credentials.get("redirect", None) is not None:
        return jsonify(credentials)

    # Get gcal service
    service = get_gcal_service(credentials)

    # Get google calendar list
    calendar_list = service.calendarList().list().execute()["items"]

    # Extract relevant info from google calendar list
    calendars = []
    for item in calendar_list:
        calendars.append({"name": item["summary"], "id": item["id"]})

    return jsonify({"calendar_list": calendars})


@gcal.route('/calendar_events')
@signin_required
def calendar_events():
    """Route controller fetches events for a calendar in Google Calendar.
    """
    # Get params from query string
    cal_id = request.args.get('id')
    now = request.args.get('now')

    # Return array of calendar events
    return jsonify(get_calendar_events(cal_id, now))


def get_google_auth_uri_for_user(google_id):
    """Gets Google authentication uri for connected user.

        Keyword arguments:
        N/A

        Returns: Google authentication URI
    """
    # Check if user already has a refresh token
    refresh_token = get_connected_user_refresh_token(google_id)

    if refresh_token is None:
        flow = OAuth2WebServerFlow(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            scope=GOOGLE_CALENDAR_API,
            redirect_uri=REDIRECT_URI,
            approval_prompt=APPROVAL_PROMPT)
    else:
        flow = OAuth2WebServerFlow(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            scope=GOOGLE_CALENDAR_API,
            redirect_uri=REDIRECT_URI)

    return flow.step1_get_authorize_url()


def get_calendar_events(cal_id, now):
    """Fetches events for a google calendar

        Returns: array of event objects from a google calendar with cal id
    """
    # Check the oauth creds and refresh if necessary
    credentials = try_get_oauth_creds()
    if credentials.get("redirect", None) is not None:
        return jsonify(credentials)

    # Get gcal service
    service = get_gcal_service(credentials)

    events = service.events().list(
        calendarId=cal_id, timeMin=now, singleEvents=True,
        orderBy="startTime").execute()
    return events


def try_get_oauth_creds():
    """Tries to get the google OAuth creds for a user.

        Returns: OAuth credentials for connected user
    """
    # Get google credentials from session
    credentials = session.get('gcal_credentials', None)

    # If google credentials don't exist, get them
    if credentials is None:
        return {"redirect": url_for('gcal.authenticate')}

    # Get fresh access token if connected access token is expired
    credentials["access_token"] = get_gcal_access_token(credentials)

    # If access token doesn't exist or can't be refreshed, re-authenticate
    if credentials["access_token"] is None:
        return {"redirect": url_for('gcal.authenticate')}

    return credentials


def is_valid_gcal_access_token(token):
    """Validates Google access token.

        Keyword arguments:
        token -- Google access token

        Returns: True iff token is valid
    """
    # Build URL for token info API
    token_info = requests.get(
        '{0}?access_token={1}'.format(GOOGLE_TOKEN_INFO_API, token))

    # Return true if google access token still valid
    return token_info.ok and token_info.json()['expires_in'] > 100


def refresh_gcal_access_token(refresh_token):
    """Refreshes Google access token.

        Keyword arguments:
        refresh_token -- Google refresh token

        Returns: fresh Google access token
    """
    # Construct dictionary representing POST headers
    headers = dict(
        grant_type="refresh_token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        refresh_token=refresh_token
    )

    # Get new access token from Google
    token = requests.post(GOOGLE_TOKEN_API, headers).json()

    return token.get("access_token", None)


def get_gcal_access_token(credentials):
    """Gets Google access token using credentials.

        Keyword arguments:
        credentials -- Google credentials

        Returns: Google access token
    """
    # Get access token from credentials
    token = credentials["access_token"]
    valid_token = True

    # Check with Google if access token is valid
    if token:
        valid_token = is_valid_gcal_access_token(token)

    # If acess token is invalid or doesn't exist, refresh it and return it
    if not token or not valid_token:
        google_id = session.get("google_id", None)
        refresh_token = get_connected_user_refresh_token(google_id)
        token = refresh_gcal_access_token(refresh_token)

    return token


def get_gcal_service(credentials):
    """Gets Google Calenndar service with credentials.

        Keyword arguments:
        credentials -- Google credentials

        Returns: Google Calendar service
    """

    # Update gcal_credentials in session
    session["gcal_credentials"] = credentials

    # Build access token credentials
    credentials = AccessTokenCredentials(credentials.get("access_token", None),
                                         credentials.get('user_agent', None))

    # I think this builds a URL that can be used for
    # retrieving the google calendar shit
    http = httplib2.Http()
    http = credentials.authorize(http)

    return build_from_document(GCAL_DISCOVERY, http=http)


@cache.memoize(timeout=10)
def get_connected_user_refresh_token(google_id):
    """Gets the refresh token for the connectedly logged in user.

    Keyword arguments:
    google_id -- the google id of the user

    Returns: refresh token for connected user
    """
    return users.find_one(
        {"google_id": google_id},
        {"gcal_refresh_token": 1, "_id": 0}).get("gcal_refresh_token")
