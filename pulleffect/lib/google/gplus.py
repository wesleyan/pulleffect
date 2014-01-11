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
from oauth2client.file import Storage
from pulleffect.lib.utilities import mongo_connection
from pulleffect.lib.utilities import signin_required

gplus = Blueprint('gplus', __name__, template_folder='templates')


# Build Google Calendar url
flow = flow_from_clientsecrets('./pulleffect/config/google_client_secrets.json',
                               scope='https://www.googleapis.com/auth/plus.login',
                               redirect_uri='http://localhost:5000/gplus/signin')
auth_uri = flow.step1_get_authorize_url()
storage = Storage('./pulleffect/config/gplus_creds')

# Sign in user
@gplus.route('/signin')
def signin():
    if (request.args.get('code')):
        credentials = flow.step2_exchange(request.args.get('code'))
        session['gplus_access_token'] = credentials.access_token
        storage.put(credentials)
        session['signed_in'] = True 
        flash('Successfully signed in', 'success')
	    # return jsonify({'redirect':url_for('index')})
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