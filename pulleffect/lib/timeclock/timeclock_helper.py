import cx_Oracle
import pulleffect.lib.timeclock.timeclock_objects as tc_obj
import pulleffect.lib.timeclock.timeclock_depts as tc_depts
from pulleffect.lib.utilities import wes_timeclock_pool
from pulleffect.lib.utilities import represents_int
from datetime import datetime


def parse_request(request):
    """Parses request parameters from URL

    Keyword arguments:
        request -- HTTP request containing parameters

    Returns:
        TimeclockRequest -- an object representing Oracle SQL query with
                            named parameters
    """
    # Default 'now' and 'begin_of_month_seconds' query parameters
    now = datetime.now()
    now_seconds = now.strftime('%s')
    begin_of_month_seconds = datetime(now.year, now.month, 1).strftime('%s')

    # Named parameters for query
    username = request.args.get('username', None)
    time_in = request.args.get('time_in', None)
    time_out = request.args.get('time_out', None)
    departments = request.args.get('depts', None)
    limit = request.args.get('limit', 50)

    error_message = []

    # Parse limit
    if not represents_int(limit):
        error_message.append({'error': "invalid parameter: 'limit'"})
    else:
        limit = abs(int(limit))

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

    return tc_obj.TimeclockRequest(
        username, time_in, time_out, job_ids, limit, error_message)


def build_timeclock_entries(cursor):
    """Build TimeclockEntry from cursor

    Keyword arguments:
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

    Keyword arguments:
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
        return {'timeclock_entries': tc_entries}

    # Catch exceptions that may be thrown during connection to database
    except cx_Oracle.DatabaseError, exception:
        error, = exception
        session_killed = 28

        # Drop the connection if the query fails
        if error.code == session_killed:
            wes_timeclock_pool.drop(connection)

        # Return error
        return {'error': str(error)}

    # TODO(arthurb): My return statement is wrong here. Please read about
    # try-except-else statements.
    else:
        cursor.close()
        wes_timeclock_pool.release(connection)
        return {'error': 'not sure what dafuz happened'}
