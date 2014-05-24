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


from flask import Blueprint
from flask import jsonify
from flask import request
from flask import make_response
from pulleffect.lib.utilities import require_signin
import moment
import pulleffect.lib.timeclock.timeclock_depts as tc_depts
import pulleffect.lib.timeclock.timeclock_helper as tc_helper
import pulleffect.lib.timeclock.timeclock_objects as tc_obj


timeclock = Blueprint('timeclock', __name__, template_folder='templates')


@timeclock.route('')
@require_signin
def index():
    """Tries to get timeclock entries from Oracle db

    Returns: An array of timeclock entries of the form:

    Example Response:

            [{
                'username': 'aburkart',
                'dept': 'om',
                'time_in': <timestamp>,
                'time_out': <timestamp>
            }]

        or

            {
                'error' <some indicative error message>
            }


    Example route: 'http://localhost:3000/timeclock?username=aburkart'
    """
        # Default time range
    now_secs = str(moment.now().strftime('%s'))
    begin_of_month_secs = str(moment.now().replace(days=1).strftime('%s'))

    # Get named parameters from query, otherwise default
    username = request.args.get('username', None)
    time_in = request.args.get('time_in', begin_of_month_secs)
    time_out = request.args.get('time_out', now_secs)
    departments = request.args.get('depts', tc_depts.get_all_job_ids())
    limit = request.args.get('limit', '50')
    clocked_in = request.args.get('clocked_in', False)

    error_message = []

    # Parse clock_in
    clocked_in = False if not clocked_in else clocked_in.lower() == 'true'

    # Parse username
    if username and isinstance(username, unicode):
        username = username.encode('ascii', 'replace')
        if '?' in username:
            error_message.append({'error': "No unicode allowed: 'username'"})

    # Parse time_in
    if not time_in.isdigit():
        error_message.append({'error': "Invalid parameter: 'time_in'"})

    # Parse time_out
    if clocked_in:
        time_out = None
        time_in = (moment
                   .now()
                   .replace(hours=0, minutes=0, seconds=0)
                   .strftime('%s'))
    elif not time_out.isdigit():
        error_message.append({'error': "Invalid parameter: 'time_out'"})

    # Parse departments
    job_ids = []
    dept_errors = []
    if not isinstance(departments, basestring):
        job_ids = departments
    else:
        departments = departments.replace(" ", "")
        departments = departments.encode('ascii', 'replace')

        if '?' in departments:
            error_message.append({'error': "No unicode allowed: 'depts'"})
        else:
            # Remove parentheses from ends of array
            departments = departments[1:-1].split(',')

            # Map department names to their respective job_id
            for dept in departments:
                job_id = tc_depts.get_job_id(dept, None)
                if not job_id:
                    dept_errors.append(dept)
                job_ids.append(job_id)

    # Parse limit
    if not limit.isdigit():
        error_message.append({'error': "Invalid parameter: 'limit'"})
    else:
        limit = 0 if clocked_in else abs(int(limit))

    # Add any dept_errors to error_message
    if dept_errors:
        dept_errors = str(dept_errors)
        error_message.append({
            'error': "Invalid parameter: 'depts': {0}".format(dept_errors)})

    # If timeclock request has errors, return them to the user
    if len(error_message) > 0:
        return make_response(jsonify(error_message), 400)

    # Build an oracle query from the request
    timeclockOracleQuery = tc_obj.TimeclockOracleQuery(
        username, time_in, time_out, job_ids, limit, clocked_in)

    # Try to get timeclock entries with the timeclock oracle query
    tc_entries = tc_helper.try_get_timeclock_entries(timeclockOracleQuery)

    # Fetches timeclock entries from Oracle db
    return jsonify(tc_entries)
