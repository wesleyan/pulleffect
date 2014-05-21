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
from pulleffect.lib.utilities import signin_required
from pulleffect.lib.utilities import wes_timeclock_pool
from datetime import datetime
import cx_Oracle
import pulleffect.lib.timeclock.timeclock_objects as tc_obj
import pulleffect.lib.timeclock.timeclock_depts as tc_depts

timeclock = Blueprint('timeclock', __name__, template_folder='templates')


def get_parsed_request(request):
    """Parses request parameters from URL

    Args:
        request -- HTTP request containing parameters

    Returns:
        TimeclockRequest -- an object representing Oracle SQL query with
                            named parameters
    """
    # Default query parameters
    now = datetime.now()
    now_seconds = now.strftime('%s')
    begin_of_month_seconds = datetime(now.year, now.month, 1).strftime('%s')

    # Named parameters for query
    username = request.args.get('username', None)
    time_in = request.args.get('time_in', None)
    time_out = request.args.get('time_out', None)
    departments = request.args.get('depts', None)

    error_message = []

    # Parse username
    if username is not None and not isinstance(username, str):
        username = username.encode('ascii', 'replace')
        if '?' in username:
            error_message.append({'error': "no unicode allowed: 'username'"})

    # Parse time in
    if time_in is None:
        time_in = str(begin_of_month_seconds)
    elif not time_in.isdigit():
        error_message.append({'error': "invalid parameter: 'time_in'"})

    # Parse time out
    if time_out is None:
        time_out = str(now_seconds)
    elif not time_out.isdigit():
        error_message.append({'error': "invalid parameter: 'time_out'"})

    # Parse departments
    job_ids = []
    if departments is None:
        job_ids = tc_depts.get_all_job_ids()
    else:
        departments = departments.replace(" ", "")
        departments = departments.encode('ascii', 'replace')
        if '?' in departments:
            error_message.append({'error': "no unicode allowed: 'depts'"})
        else:
            # Remove parentheses from ends of array
            departments = departments[1:-1].split(',')

            # Map department names to their respective job_id
            dept_errors = []
            for i in range(len(departments)):
                job_id = tc_depts.get_job_id(departments[i], None)
                if job_id is None:
                    dept_errors.append(departments[i])
                job_ids.append(job_id)

            # Return error if invalid department names given
            if len(dept_errors) > 0:
                err = "Invalid parameter: 'depts': {0}"
                err.format(str(dept_errors))
                error_message.append({'error': err})

    return tc_obj.TimeclockRequest(username, time_in, time_out, error_message)


def build_timeclock_entries(cursor):
    """Build TimeclockEntry from cursor

    Args:
        cursor -- tuple representation of Oracle SQL query results

    Returns:
        array -- An array containing TimeclockEntry objects
    """
    # Build array of timeclock entries retrieved in cursor
    tc_entries = []

    # Add timeclock entry objects to array
    for row in cursor:
        username = row[0]
        time_in = row[1]
        time_out = row[2]
        dept = tc_depts.get_dept(str(row[3]), "???")
        note = row[4]
        tc_entries.append(
            tc_obj.TimeclockEntry(username, time_in, time_out, dept, note))
    return tc_entries


def try_get_timeclock_entries(timeclockOracleQuery):
    """Tries to get timeclock entries from Oracle db

    Args:
    timeclockOracleQuery -- object representing Oracle SQL and
                            its named parameters

    Returns:
        Response -- A list of timeclock entries of the form:

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
    """
    # Grab connection from pool of connections
    connection = wes_timeclock_pool.acquire()
    try:
        # Get cursor from connection
        cursor = connection.cursor()

        # Execute query against db
        cursor.execute(timeclockOracleQuery.query,
                       timeclockOracleQuery.named_params)

        # Get timeclock entries from cursor
        tc_entries = build_timeclock_entries(cursor)

        # Serialize array of timeclock entries
        tc_entries = [entry.serialize() for entry in tc_entries]
        return jsonify({'timeclock_entries': tc_entries})

    # Catch exceptions that may be thrown during connection to database
    except cx_Oracle.DatabaseError, exception:
        error, = exception
        session_killed = 28

        # Drop the connection if the query fails
        if error.code == session_killed:
            wes_timeclock_pool.drop(connection)

        # Return error
        return jsonify(error=str(error))

    # Do this when something crazy unknown happens
    else:
        cursor.close()
        wes_timeclock_pool.release(connection)
        return jsonify(error="not sure what dafuz happened")


@timeclock.route('')
@signin_required
def index():
    """Tries to get timeclock entries from Oracle db

    Returns:
        Response: A list of timeclock entries of the form:

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
    # Get parsed Oracle timeclock request
    timeClockRequest = get_parsed_request(request)

    # If timeclock request has errors, return them to the user
    if len(timeClockRequest.error_message) > 0:
        return make_response(jsonify(timeClockRequest.error_message), 400)

    # Build an oracle query from the request
    timeclockOracleQuery = tc_obj.TimeclockOracleQuery(
        timeClockRequest.username, timeClockRequest.time_in,
        timeClockRequest.time_out, timeClockRequest.job_ids)

    # Fetches timeclock entries from Oracle db
    try_get_timeclock_entries(timeclockOracleQuery)
