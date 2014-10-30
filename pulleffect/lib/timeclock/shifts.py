# Copyright (C) 2014 Wesleyan University
#
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

import logging
import moment
import pulleffect.config.env as env
import pulleffect.lib.google.gcal_helper as gc_helper
import pulleffect.lib.timeclock.timeclock_depts as tc_depts
import pulleffect.lib.timeclock.timeclock_helper as tc_helper
import pulleffect.lib.timeclock.timeclock_objects as tc_obj
from flask import Blueprint
from flask import jsonify
from flask import redirect
from flask import request
from flask import url_for
from pulleffect.lib.utilities import require_signin
from pulleffect.lib.utilities import Widgets


shifts = Blueprint('shifts', __name__, template_folder='templates')


@shifts.route('/authenticate')
@require_signin
def authenticate():
    """Authenticates system user with Google Calendars.
    """
    # Get the system user
    username = env.config['sys_user']
    assert username

    # Get auth URI for system user
    auth_uri = gc_helper.get_google_auth_uri_from_username(
        username, Widgets.SHIFTS)
    return redirect(auth_uri)


@shifts.route('/oauth2callback')
@require_signin
def oauth2callback():
    """Route controller completes Google Calendar authentication.
    """
    # Get code from query string
    code = request.args.get('code', None)

    # Validate authorization code
    gc_helper.try_validate_google_authorization_code(code, Widgets.SHIFTS)

    # Redirect to the main page of the application
    return redirect(url_for('index'))


@shifts.route('/calendar_list')
@require_signin
def calendar_list():
    """Route controller fetches array of calendars from Google Calendar.
    """
    username = env.config['sys_user']
    assert username

    # Get calendar list
    calendars = gc_helper.get_calendar_list(username, Widgets.SHIFTS)

    # Return list of calendars
    return jsonify(calendars)


@shifts.route('')
@require_signin
def index():
    """Route controller fetches shifts info.
    """
    # Get params from query string
    cal_id = gc_helper.SHIFTS_GCAL 

    # Set default values
    timeMin = moment.now().replace(
        hours=0, minutes=0, seconds=0).format("YYYY-MM-DDTHH:mm:ssZ")
    timeMax = moment.now().add('days', 1).replace(
        hours=0, minutes=0, seconds=0).format("YYYY-MM-DDTHH:mm:ssZ")
    username = env.config['sys_user']
    assert username

    # Get calendar event items
    events = gc_helper.get_calendar_events(
        cal_id, timeMin, timeMax, username, Widgets.SHIFTS)

    if events.get('redirect'):
        return jsonify(events)

    events = events.get('items', {})
    events = dict(
        (event.get('description'), dict(
            start=event.get('start').get('dateTime'),
            end=event.get('end').get('dateTime')))
        for event in events
    )
    #changing from ISO8601 to timestamp, for Oracle
    timeMin = moment.date(timeMin, "YYYY-MM-DDTHH:mm:ssZ").strftime('%s')
    timeclockOracleQuery = tc_obj.TimeclockOracleQuery(
        username=None, time_in=timeMin, time_out=timeMin,
        job_ids=tc_depts.get_all_job_ids(), limit=0, clocked_in=True)

    tc_entries = (tc_helper
                  .try_get_timeclock_entries(timeclockOracleQuery)
                  .get('timeclock_entries'))
    logging.info('tc_entries : {0}'.format(tc_entries))
    scheduled = {}
    not_scheduled = {}
    if tc_entries:
        for entry in tc_entries:
            username = entry.get('username')
            note = entry.get('note')
            time_in = entry.get('time_in')
            dept = entry.get('dept')

            # Try to get event corresponding to timeclock entry
            event = events.get(username, None)

            # Flesh out event
            if event:
                event['note'] = note
                event['clocked_in'] = time_in
                event['dept'] = dept

                # Add event to `scheduled` dict
                scheduled[username] = event

                # Remove event
                events.pop(username)
            else:
                not_scheduled[username] = dict(
                    note=note, clocked_in=time_in, dept=dept)

    # Any event remaining in events dict is not clocked in
    not_clocked_in = events
    # Returns array of shifts
    return jsonify({
        "shifts": dict(scheduled=scheduled, not_clocked_in=not_clocked_in,
                       not_scheduled=not_scheduled)})
