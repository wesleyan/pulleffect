
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

import pulleffect.lib.google.gcal_helper as gc_helper
import moment
from flask import Blueprint
from flask import jsonify
from flask import redirect
from flask import request
from flask import session
from flask import url_for
from pulleffect.lib.utilities import require_signin
from pulleffect.lib.utilities import Widgets


gcal = Blueprint('gcal', __name__, template_folder='templates')


@gcal.route('/authenticate')
@require_signin
def authenticate():
    """Route controller authenticates user with Google Calendar.
    """
    # Get username of connected user
    username = session.get("username", None)
    assert username

    # Get auth URI from username
    auth_uri = gc_helper.get_google_auth_uri_from_username(
        username, Widgets.GCAL)
    return redirect(auth_uri)


@gcal.route('/oauth2callback')
@require_signin
def oauth2callback():
    """Route controller completes Google Calendar authentication.
    """
    # Get code from query string
    code = request.args.get('code', None)

    # Validate authorization code
    gc_helper.try_validate_google_authorization_code(code, Widgets.GCAL)

    # Redirect to the main page of the application
    return redirect(url_for('index'))


@gcal.route('/calendar_list')
@require_signin
def calendar_list():
    """Route controller fetches array of calendars from Google Calendar.
    """
    username = session.get('username', None)
    assert username

    # Get calendar list
    calendars = gc_helper.get_calendar_list(username, Widgets.GCAL)

    # Return list of calendars
    return jsonify(calendars)


@gcal.route('/calendar_events')
@require_signin
def calendar_events():
    """Route controller fetches events for a calendar in Google Calendar.
    """
    # Get params from query string
    cal_id = request.args.get('id')
    timeMin = request.args.get('now')
    timeMax = moment.now().add('days', 1).replace(
        hours=0, minutes=0, seconds=0).format("YYYY-MM-DDTHH:mm:ssZ")
    username = session.get('username', None)
    assert username

    # Get calendar event items
    events = gc_helper.get_calendar_events(
        cal_id, timeMin, timeMax, username, Widgets.GCAL)

    # Return array of calendar events
    return jsonify(events)
