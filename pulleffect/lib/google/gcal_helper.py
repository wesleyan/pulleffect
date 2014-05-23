import httplib2
import json
import logging
import pulleffect.config.env as env
import requests
from apiclient.discovery import build_from_document
from flask import request
from flask import session
from flask import url_for
from pulleffect.lib.utilities import mongo_connection
from pulleffect.lib.utilities import cache
from pulleffect.lib.utilities import Widgets
from oauth2client.client import AccessTokenCredentials
from oauth2client.client import OAuth2WebServerFlow

# This is only necessary if you want to make it clear which module is logging
gcal_logger = logging.getLogger('gcal')

# Get users mongo collection
users = mongo_connection.users

google_client_secrets = json.load(open(env.config["google_client_secrets"]))
google_client_secrets = google_client_secrets.get("web")

CLIENT_ID = google_client_secrets.get("client_id")
CLIENT_SECRET = google_client_secrets.get("client_secret")
GOOGLE_TOKEN_API = "https://accounts.google.com/o/oauth2/token"
GOOGLE_CALENDAR_API = "https://www.googleapis.com/auth/calendar"
GOOGLE_TOKEN_INFO_API = "https://www.googleapis.com/oauth2/v1/tokeninfo"
GCAL_DISCOVERY = json.load(open(env.config["gcal_discovery"]))
REDIRECT_URI = '{0}/gcal/oauth2callback'.format(env.config['home_url'])
APPROVAL_PROMPT = 'force'


def get_calendar_list(username, widget):
    """Fetches list of google calendars for connected user.

        Returns: array of calendars from google account.
    """
    # Get google credentials
    credentials = get_google_creds(username, widget)

    # Check the oauth creds and refresh if necessary
    credentials = validate_and_refresh_creds(credentials)
    gcal_logger.info("Validated credentials: {0}".format(credentials))
    if credentials.get("redirect", None):
        return credentials

    # Set appropriate credentials
    set_google_creds(username, credentials, widget)

    # Get gcal service
    service = get_gcal_service_from_credentials(credentials)

    # Get google calendar list
    calendar_list = service.calendarList().list().execute()["items"]

    # TODO(arthurb): Change into a cool one-liner; maybe use lambda calc
    # Extract relevant info from google calendar list
    calendars = []
    for item in calendar_list:
        calendars.append({"name": item["summary"], "id": item["id"]})

    return {"calendar_list": calendars}


def get_calendar_events(cal_id, timeMin, timeMax, username, widget):
    """Fetches events for a google calendar

        Keyword arguments:
            cal_id -- id of calendar to fetches
            now -- TODO(arthurb): What does this do?

        Returns: array of event objects from a google calendar with cal id
    """
    credentials = get_google_creds(username, widget)

    # Check the oauth creds and refresh if necessary
    credentials = validate_and_refresh_creds(credentials)
    gcal_logger.info("Validated credentials: {0}".format(credentials))
    if credentials.get("redirect", None):
        return credentials

    set_google_creds(username, credentials, widget)

    # Get gcal service
    service = get_gcal_service_from_credentials(credentials)

    events = service.events().list(
        calendarId=cal_id, timeMin=timeMin, timeMax=timeMax, singleEvents=True,
        orderBy="startTime").execute()
    return events


def try_validate_google_authorization_code(code, widget):
    """Validated authorization code retrieved from Google.

        Keyword arguments:
            code -- authorization code retrieved from Google
    """
    if code:
        # Exchange authorization code for credentials from Google
        credentials = exchange_code_for_credentials(code)
        assert credentials

        # Get username for connected user
        username = session.get("username", None)
        assert username
        gcal_logger.info("Fetched username: {0}".format(username))

        # Get Google refresh token for connected user
        refresh_token = get_refresh_token_from_username(username)
        gcal_logger.info("Fetched refresh token: {0}".format(refresh_token))

        # If refresh token is invalid, refresh it
        if not refresh_token:
            refresh_token = credentials.refresh_token
        gcal_logger.info("Updated refresh token: {0}".format(refresh_token))

        # Update connected user's refresh token
        users.update(
            {"username": username},
            {"$set": {
                "google_refresh_token": refresh_token,
                "google_user_agent": credentials.user_agent
            }},
            upsert=False)

        google_creds = {
            "access_token": credentials.access_token,
            "user_agent": credentials.user_agent
        }

        # Update Google credentials in session for connected user
        set_google_creds(username, google_creds, widget)


def get_google_creds(username, widget):
    """Gets Google credentials based on username.

        Keyword arguments:
        username -- username of user
        route -- from where the request is being made

        Example:
            get_google_creds('dummy', Widgets.SHIFTS)
    """
    if widget == Widgets.SHIFTS:
        gcal_logger.info("Retrieving sys_user google creds.")
        return session.get('sys_google_creds', None)
    else:
        gcal_logger.info("Retrieving connected user google creds.")
        return session.get('google_creds', None)


def set_google_creds(username, credentials, widget):
    """Sets Google credentials based on username.

        Keyword arguments:
        username -- username of user
    """
    if widget == Widgets.SHIFTS:
        gcal_logger.info("Updating sys_user google creds.")
        session['sys_google_creds'] = credentials
    else:
        gcal_logger.info("Updating connected user google creds.")
        session['google_creds'] = credentials


def get_gcal_service_from_credentials(credentials):
    """Gets Google Calendar service with credentials.

        Keyword arguments:
        credentials -- Google credentials

        Returns: Google Calendar service
    """
    # Build access token credentials
    credentials = AccessTokenCredentials(credentials.get("access_token", None),
                                         credentials.get('user_agent', None))

    # Probably builds a URL used to retrieve Google Calendar shit
    http = httplib2.Http()
    http = credentials.authorize(http)

    return build_from_document(GCAL_DISCOVERY, http=http)


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
        refresh_token = get_refresh_token_from_username(username)
        token = refresh_gcal_access_token(refresh_token)

    return token


def validate_and_refresh_creds(credentials):
    """Tries to get the google OAuth creds for connected user.
    """
    # If google credentials don't exist, get them
    if not credentials:
        return {"redirect": url_for('gcal.authenticate')}

    # Get fresh access token if connected access token is expired
    credentials["access_token"] = get_gcal_access_token(credentials)

    # If access token doesn't exist or can't be refreshed, re-authenticate
    if not credentials["access_token"]:
        return {"redirect": url_for('gcal.authenticate')}

    return credentials


@cache.memoize(timeout=10)
def get_refresh_token_from_username(username):
    """Gets the refresh token for the connectedly logged in user.

    Keyword arguments:
    username -- the google id of the user

    Returns: refresh token for connected user
    """
    user = users.find_one(
        {"username": username}, {"google_refresh_token": 1, "_id": 0})
    return None if not user else user.get("google_refresh_token")


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
        gcal_logger.warning(error_message.format(e.message))
        return None


def get_google_auth_uri_from_username(username):
    """Gets Google authentication uri for connected user.

        Keyword arguments:
            username -- Google id for connected user

        Returns: Google authentication URI
    """
    # Check if user already has a refresh token
    refresh_token = get_refresh_token_from_username(username)

    if not refresh_token:
        gcal_logger.info("Forced approval because refresh token was missin.")
        flow = OAuth2WebServerFlow(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            scope=GOOGLE_CALENDAR_API,
            redirect_uri=REDIRECT_URI,
            approval_prompt=APPROVAL_PROMPT)
    else:
        gcal_logger.info("Using refresh token to get new access token.")
        flow = OAuth2WebServerFlow(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            scope=GOOGLE_CALENDAR_API,
            redirect_uri=REDIRECT_URI)

    return flow.step1_get_authorize_url()


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


def get_gcal_service(credentials):
    """Gets Google Calendar service with credentials.

        Keyword arguments:
        credentials -- Google credentials

        Returns: Google Calendar service
    """

    # Update google_creds in session
    session["google_creds"] = credentials
    gcal_logger.info("Updated credentials: {0}".format(credentials))

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
