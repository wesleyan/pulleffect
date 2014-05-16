from apiclient.discovery import build_from_document
from flask import Blueprint
from flask import jsonify
from flask import redirect
from flask import request
from flask import session
from flask import url_for
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import AccessTokenCredentials
from pulleffect.lib.utilities import mongo_connection
from pulleffect.lib.utilities import signin_required
from pulleffect.lib.cache import cache
from pulleffect.config.env import config
import requests
import json
import httplib2

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
    # Get Google auth uri
    auth_uri = get_google_auth_uri_for_user()
    return redirect(auth_uri)


@gcal.route('/oauth2callback')
@signin_required
def oauth2callback():
    # Get code from query string
    code = request.args.get('code')

    # If code exists in query string, then get token
    # information for connected user
    if code:
        # exchange the authorization code for user credentials
        flow = OAuth2WebServerFlow(CLIENT_ID,
                                   CLIENT_SECRET,
                                   GOOGLE_CALENDAR_API)
        flow.redirect_uri = request.base_url
        try:
            credentials = flow.step2_exchange(code)
        except Exception as e:
            print "Unable to get an access token because ", e.message

        # Get gcal refresh token
        google_id = session.get("google_id", None)
        refresh_token = get_connected_user_refresh_token(google_id)

        if refresh_token is None:
            refresh_token = credentials.refresh_token

        users.update({"google_id": google_id},
                     {"$set": {"gcal_refresh_token": refresh_token,
                      "gcal_user_agent": credentials.user_agent}},
                     upsert=False)
        session["gcal_credentials"] = {
            "access_token": credentials.access_token,
            "user_agent": credentials.user_agent}

    return redirect(url_for('index'))


@gcal.route('/calendar_list')
@signin_required
def calendar_list():
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
    events = get_calendar_events()
    return jsonify(events)


def get_calendar_events():
    # Check the oauth creds and refresh if necessary
    credentials = try_get_oauth_creds()
    if credentials.get("redirect", None) is not None:
        return jsonify(credentials)

    # Get gcal service
    service = get_gcal_service(credentials)

    calId = request.args.get('id')
    now = request.args.get('now')

    events = service.events().list(calendarId=calId,
                                   timeMin=now,
                                   singleEvents=True,
                                   orderBy="startTime").execute()
    return events


def try_get_oauth_creds():
    # Get google credentials from session
    credentials = session.get('gcal_credentials', None)

    # If google credentials don't exist, get them
    if credentials is None:
        return {"redirect": url_for('gcal.authenticate')}

    # Get fresh access token if current access token is expired
    credentials["access_token"] = get_gcal_access_token(credentials)

    # If access token doesn't exist or can't be refreshed, re-authenticate
    if credentials["access_token"] is None:
        return {"redirect": url_for('gcal.authenticate')}

    return credentials


def is_valid_gcal_access_token(token):
    # Check with google if your access token is valid
    token_info = requests.get('{0}?access_token={1}'
                              .format(GOOGLE_TOKEN_INFO_API,
                                      token))
    return token_info.ok and token_info.json()['expires_in'] > 100


def refresh_gcal_access_token(refresh_token):
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


def get_google_auth_uri_for_user():
    google_id = session.get("google_id", None)
    # Check if user already has a refresh token
    refresh_token = get_connected_user_refresh_token(google_id)

    if refresh_token is None:
        flow = OAuth2WebServerFlow(client_id=CLIENT_ID,
                                   client_secret=CLIENT_SECRET,
                                   scope=GOOGLE_CALENDAR_API,
                                   redirect_uri=REDIRECT_URI,
                                   approval_prompt=APPROVAL_PROMPT)
    else:
        flow = OAuth2WebServerFlow(client_id=CLIENT_ID,
                                   client_secret=CLIENT_SECRET,
                                   scope=GOOGLE_CALENDAR_API,
                                   redirect_uri=REDIRECT_URI)

    return flow.step1_get_authorize_url()


@cache.memoize(timeout=10)
def get_connected_user_refresh_token(google_id):
    return users.find_one({"google_id": google_id},
                          {"gcal_refresh_token": 1,
                           "_id": 0}).get("gcal_refresh_token")
