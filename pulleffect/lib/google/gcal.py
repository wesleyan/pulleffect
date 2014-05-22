
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
from pulleffect.lib.utilities import require_signin
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
@require_signin
def authenticate():
    """Route authenticates user with Google Calendar.
    """
    # Get username of connected user
    username = session.get("username", None)
    assert username is not None

    # Get auth URI from username
    auth_uri = get_google_auth_uri_for_user(username)
    return redirect(auth_uri)


@gcal.route('/oauth2callback')
@require_signin
def oauth2callback():
    """Route controller completes Google Calendar authentication.
    """
    # Get code from query string
    code = request.args.get('code', None)

    if code:
        # Exchange authorization code for credentials from Google
        credentials = exchange_code_for_credentials(code)
        assert credentials is not None

        # Get Google id for connected user
        username = session.get("username", None)
        assert username is not None

        # Get Google refresh token for connected user
        refresh_token = get_connected_user_refresh_token(username)

        # If refresh token is invalid, refresh it
        if refresh_token is None:
            refresh_token = credentials.refresh_token

        # Update connected user's refresh token
        users.update(
            {"username": username},
            {"$set": {
                "google_refresh_token": refresh_token,
                "google_user_agent": credentials.user_agent
            }},
            upsert=False)

        # Update Google credentials in session for connected user
        session["google_creds"] = {
            "access_token": credentials.access_token,
            "user_agent": credentials.user_agent
        }

    # Redirect to the main page of the application
    return redirect(url_for('index'))


@gcal.route('/calendar_list')
@require_signin
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

    # TODO(arthurb): Change into a cool one-liner; maybe use lambda calc
    # Extract relevant info from google calendar list
    calendars = []
    for item in calendar_list:
        calendars.append({"name": item["summary"], "id": item["id"]})

    return jsonify({"calendar_list": calendars})


@gcal.route('/calendar_events')
@require_signin
def calendar_events():
    """Route controller fetches events for a calendar in Google Calendar.
    """
    # Get params from query string
    cal_id = request.args.get('id')
    now = request.args.get('now')

    # Return array of calendar events
    return jsonify(get_calendar_events(cal_id, now))


def exchange_code_for_credentials(code):
    # Build OAuth2 web server flow from authorization code
    flow = OAuth2WebServerFlow(
        CLIENT_ID,
        CLIENT_SECRET,
        GOOGLE_CALENDAR_API)
    flow.redirect_uri = request.base_url

    # Get credentials from authorization code
    try:
        credentials = flow.step2_exchange(code)
        return credentials
    except Exception as e:
        error_message = "Unable to get a Google access token because {0}"
        logging.warning(error_message.format(e.message))
        return None


def get_google_auth_uri_for_user(username):
    """Gets Google authentication uri for connected user.

        Keyword arguments:
            username -- Google id for connected user

        Returns: Google authentication URI
    """
    # Check if user already has a refresh token
    refresh_token = get_connected_user_refresh_token(username)

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

        Keyword arguments:
            cal_id -- id of calendar to fetches
            now -- TODO(arthurb): What does this do?

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
    """Tries to get the google OAuth creds for connected user.
    """
    # Get google credentials from session
    credentials = session.get('google_creds', None)

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

        Returns: True iff token is valid, otherwise False
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

    # If access token is invalid or donesn't exist, refresh it and return it
    if not token or not valid_token:
        username = session.get("username", None)
        refresh_token = get_connected_user_refresh_token(username)
        token = refresh_gcal_access_token(refresh_token)

    return token


def get_gcal_service(credentials):
    """Gets Google Calendar service with credentials.

        Keyword arguments:
        credentials -- Google credentials

        Returns: Google Calendar service
    """

    # Update google_creds in session
    session["google_creds"] = credentials

    # Build access token credentials
    credentials = AccessTokenCredentials(credentials.get("access_token", None),
                                         credentials.get('user_agent', None))

    # Probably builds a URL used to retrieve Google Calendar shit
    http = httplib2.Http()
    http = credentials.authorize(http)

    return build_from_document(GCAL_DISCOVERY, http=http)


@cache.memoize(timeout=10)
def get_connected_user_refresh_token(username):
    """Gets the refresh token for the connectedly logged in user.

    Keyword arguments:
    username -- the google id of the user

    Returns: refresh token for connected user
    """
    user = users.find_one(
        {"username": username}, {"google_refresh_token": 1, "_id": 0})
    return user if not user else user.get("google_refresh_token")
