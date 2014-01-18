from flask import Blueprint
from flask import redirect
from flask import request
from flask import session
from flask import url_for
from flask import flash
from oauth2client.client import flow_from_clientsecrets
from pulleffect.lib.utilities import mongo_connection
from pulleffect.lib.utilities import signin_required
import requests
from urllib import urlencode

gplus = Blueprint('gplus', __name__, template_folder='templates')


# Build Google Calendar url
flow = flow_from_clientsecrets('./pulleffect/config/google_client_secrets.json', 
    scope='https://www.googleapis.com/auth/plus.login https://www.googleapis.com/auth/userinfo.email', 
    redirect_uri='http://localhost:5000/gplus/signin')
auth_uri = flow.step1_get_authorize_url()


# Sign in user
@gplus.route('/signin')
def signin():
    if (request.args.get('code')):
        credentials = flow.step2_exchange(request.args.get('code'))
        session['gplus_access_token'] = credentials.access_token

        # Get access token, refresh token, and google id from credentials
        google_access_token = credentials.access_token
        google_refresh_token = credentials.refresh_token
        google_id = credentials.id_token["sub"]

        # Get users collection
        users = mongo_connection.users

        # Fetch user from mongodb
        user = users.find_one({"google_id":google_id})

        # Sign in case
        if user != None:
            google_email = user["google_email"]
            google_name = user["google_name"]
            # Make sure we don't overwrite refresh_token with None object
            if google_refresh_token == None:
            	google_refresh_token = user["google_refresh_token"]
                users.update({"google_id":google_id}, {"$set": {"google_access_token":google_access_token, "google_refresh_token":google_refresh_token}})

        # Sign up case
        else: 
            # Get user's email and user name 
            req = requests.get('https://www.googleapis.com/plus/v1/people/' + str(google_id) + '?' + urlencode({"access_token": google_access_token}))
            req = req.json()
            google_email = req["emails"].pop()["value"]
            google_name = req["displayName"]
            users.insert({"google_id":google_id, "google_access_token":google_access_token, "google_refresh_token":google_refresh_token, "google_email":google_email, "google_name":google_name})

        session['signed_in'] = True 
        session['google_email'] = google_email
        session["google_name"] = google_name
        flash('Hello ' + google_name + ', you have successfully signed in', 'success')
        return redirect(url_for('index'))
    if (request.args.get('error')):
    	flash('Google authentication failed!\nError:' + str(request.args.get('error')), 'error')
        session['gplus_access_token'] = None
        return redirect(url_for('index'))
    return redirect(auth_uri)


# Sign out user
@gplus.route('/signout', methods=['POST'])
@signin_required
def signout():
    session.pop('signed_in', None)
    flash('You are signed out.', 'success')
    return redirect(url_for('index'))