from flask import Blueprint
from flask import redirect
from flask import request
from flask import session
from flask import url_for
from flask import flash
from oauth2client.client import flow_from_clientsecrets
from pulleffect.lib.utilities import mongo_connection
from pulleffect.lib.utilities import signin_required
from pulleffect.config.env import config
import requests
from urllib import urlencode

gplus = Blueprint('gplus', __name__, template_folder='templates')

GOOGLE_PLUS_API = 'https://www.googleapis.com/auth/plus.login'
GOOGLE_USERINFO_API = 'https://www.googleapis.com/auth/userinfo.email'
GOOGLE_PLUS_API_ROUTE = 'https://www.googleapis.com/plus/v1/people/'
REDIRECT_URI = config['home_url'] + '/gplus/signin'

# Build Google Calendar url
scope = "{0} {1}".format(GOOGLE_PLUS_API, GOOGLE_USERINFO_API)
flow = flow_from_clientsecrets(config['google_client_secrets'],
                               scope=scope,
                               redirect_uri=REDIRECT_URI)
auth_uri = flow.step1_get_authorize_url()

# Get users collection
users = mongo_connection.users


# Sign in user
@gplus.route('/signin')
def signin():
    if (request.args.get('code')):
        credentials = flow.step2_exchange(request.args.get('code'))
        session['gplus_access_token'] = credentials.access_token

        # Get access token, refresh token, and google id from credentials
        gplus_access_token = session.get('gplus_access_token')
        gplus_refresh_token = credentials.refresh_token
        google_id = credentials.id_token["sub"]

        # Fetch user from mongodb
        user = users.find_one({"google_id": google_id})

        # Sign up case
        if user is None:
            # Get user's email and user name
            urlencoded_access_token = urlencode({"access_token":
                                                 gplus_access_token})
            req = requests.get('{0}{1}?{2}'
                          .format(GOOGLE_PLUS_API_ROUTE,
                                  str(google_id),
                                  urlencoded_access_token))
            req = req.json()

            # TODO(Arthur): address edge case when
            # people have more than one email?
            google_email = req["emails"].pop()["value"]
            google_name = req["displayName"]
            users.insert({"google_id": google_id,
                          "gplus_refresh_token": gplus_refresh_token,
                          "google_email": google_email,
                          "google_name": google_name})
        # Sign in case
        else:
            google_email = user.get("google_email")
            google_name = user.get("google_name")

            # Make sure we don't overwrite refresh_token with None object
            if gplus_refresh_token is None:
                gplus_refresh_token = user.get("gplus_refresh_token")
            users.update(
                {"google_id": google_id},
                {"$set": {"gplus_refresh_token": gplus_refresh_token}})

        #Does not authenticate if email is not from wesleyan.edu
        if not google_email.endswith("@wesleyan.edu"):
            flash('You must use your Wesleyan email adress', 'error')
            return redirect(url_for('index'))
        session['signed_in'] = True
        session['google_email'] = google_email
        session['google_name'] = google_name
        session['google_id'] = google_id
        flash('Welcome ' + google_name, 'success')
        return redirect(url_for('index'))

    # Handle error
    if (request.args.get('error')):
        # Create an error message
        error_message = 'Google authentication failed!\nError: {0}'
        error_message = error_message.format(request.args.get('error'))

        # Show error message to user
        flash(error_message, 'error')

        # Remove access token from the session
        session['gplus_access_token'] = None
        return redirect(url_for('gplus.signin'))
    return redirect(auth_uri)


# Sign out user
@gplus.route('/signout')
@signin_required
def signout():
    session.pop('signed_in', None)
    flash('You are signed out.', 'success')
    return redirect(url_for('index'))
