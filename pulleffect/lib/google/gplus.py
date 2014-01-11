from apiclient.discovery import build
from flask import Blueprint
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flask import flash
import httplib2
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import AccessTokenRefreshError
from pulleffect.lib.utilities import mongo_connection
from pulleffect.lib.utilities import signin_required

gplus = Blueprint('gplus', __name__, template_folder='templates')


# Build Google Calendar url
flow = flow_from_clientsecrets('./pulleffect/config/google_client_secrets.json',
                               scope='https://www.googleapis.com/auth/plus.login',
                               redirect_uri='http://localhost:5000/gplus/signin')
auth_uri = flow.step1_get_authorize_url()


# Sign in user
@gplus.route('/signin')
def signin():
    if (request.args.get('code')):
        credentials = flow.step2_exchange(request.args.get('code'))
        session['gplus_access_token'] = credentials.access_token

        gplus_access_token = credentials.access_token
        gplus_refresh_token = credentials.refresh_token
        gplus_id = credentials.id_token["sub"]

        users = mongo_connection.users
        refresh_token = users.find_one({"id":gplus_id}, {"gplus_refresh_token":1})
        if gplus_refresh_token == None:
        	gplus_refresh_token = refresh_token

       	users.update({"gplus_id":credentials.id_token["sub"]}, {"$set": {"gplus_access_token":gplus_access_token, "gplus_refresh_token":gplus_refresh_token, "gplus_id":gplus_id}}, True)

        session['signed_in'] = True 
        flash('Successfully signed in', 'success')
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