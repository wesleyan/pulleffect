from flask import Blueprint
from flask import jsonify
from flask import request
from flask import make_response
from pulleffect.lib.utilities import signin_required
from pulleffect.lib.utilities import wes_timeclock_pool
from pulleffect.lib.timeclock.timeclock_depts import dept_to_job_id_dict
from pulleffect.lib.timeclock.timeclock_depts import job_id_to_dept_dict
from datetime import datetime
import cx_Oracle

timeclock = Blueprint('timeclock', __name__, template_folder='templates')


# Timeclock entry model
class TimeclockEntry:
    def __init__(self, username, time_in, time_out, dept, note):
        self.username = username
        self.time_in = time_in
        self.time_out = time_out
        self.dept = dept
        self.note = note

    # Serializes the object into a dictionary so it can be jsonified
    def serialize(self):
        return {
            'username': self.username,
            'time_in': self.time_in,
            'time_out': self.time_out,
            'dept': self.dept,
            'note': self.note
        }


class TimeclockQuery:
    def __init__(self, username, time_in, time_out, job_ids):
        # The stuff that probably won't ever change
        select_clause = ("SELECT * FROM (SELECT USERNAME, TIME_IN, TIME_OUT, "
                         "JOB_ID, NOTE FROM ACLC_USDAN.NED_SHIFT ORDER BY "
                         "TIME_IN DESC) ")

        # Converts datetime objects to timestamps in SQL
        sql_timestamp = ("(TO_DATE('19700101','yyyymmdd') +"
                         " (TO_NUMBER({0})/24/60/60))")

        # Build time in and time out clauses
        time_in_clause = sql_timestamp.format(':time_in')
        time_out_clause = sql_timestamp.format(':time_out')

        # Edit later if you ever need to tweak the WHERE clause
        where_clause = "WHERE TIME_IN >={0} AND TIME_OUT <={1} AND JOB_ID IN "
        where_clause = where_clause.format(time_in_clause, time_out_clause)

        # Named params that fill in the 'where_clause'
        named_params = {'time_in': time_in, 'time_out': time_out}

        # Build SQL array with job ids
        job_id_clause = "("
        for i in range(len(job_ids)):
            job_id = 'job_id{0}'.format(str(i))
            named_params[job_id] = job_ids[i]
            job_id_clause += ":{0},".format(job_id)

        # Add job ids to WHERE clause
        where_clause += job_id_clause[:-1] + ")"

        # Append the username if it was given
        if username is not None:
            where_clause += " AND USERNAME=:username"
            named_params['username'] = username

        # Completed query
        query = "{0}{1}".format(select_clause, where_clause)

        self.query = query
        self.named_params = named_params


@timeclock.route('')
@signin_required
def index():
    # Default query parameters
    now = datetime.now()
    now_seconds = now.strftime('%s')
    begin_of_month_seconds = datetime(now.year, now.month, 1).strftime('%s')

    # Named parameters for query
    username = request.args.get('username', None)
    time_in = request.args.get('time_in', None)
    time_out = request.args.get('time_out', None)
    departments = request.args.get('depts', None)

    # Validate username
    if username is not None and not isinstance(username, str):
        username = username.encode('ascii', 'replace')
        if '?' in username:
            error_message = jsonify({'error': "no unicode allowed: username"})
            return make_response(error_message, 400)

    # Validate time in
    if time_in is None:
        time_in = str(begin_of_month_seconds)
    elif not time_in.isdigit():
        error_message = jsonify({'error': "invalid parameter: 'time_in'"})
        return make_response(error_message, 400)

    # Validate time out
    if time_out is None:
        time_out = str(now_seconds)
    elif not time_out.isdigit():
        error_message = jsonify({'error': "invalid parameter: 'time_out'"})
        return make_response(error_message, 400)

    # Validate departments
    job_ids = []
    if departments is None:
        job_ids = dept_to_job_id_dict.values()
    else:
        departments = departments.replace(" ", "")
        departments = departments.encode('ascii', 'replace')
        if '?' in departments:
            error_message = jsonify({'error': "no unicode allowed: depts"})
            return make_response(error_message, 400)

        # Remove parentheses from ends of array
        departments = departments[1:-1].split(',')

        # Map department names to their respective job_id
        dept_errors = []
        for i in range(len(departments)):
            job_id = dept_to_job_id_dict.get(departments[i], None)
            if job_id is None:
                dept_errors.append(departments[i])
            job_ids.append(job_id)

        # Return error if invalid department names given
        if len(dept_errors) > 0:
            error_message = ("Invalid parameter:"
                             " 'depts': {0}").format(str(dept_errors))
            return make_response(jsonify({'error': error_message}), 400)

    # Grab connection from pool of connections
    connection = wes_timeclock_pool.acquire()
    try:
        # Get cursor from connection
        cursor = connection.cursor()

        # Get query object
        timeclock_query = TimeclockQuery(username, time_in, time_out, job_ids)

        # Execute query against db
        cursor.execute(timeclock_query.query, timeclock_query.named_params)

        # Build array of timeclock entries retrieved in cursor
        tc_entries = []

        # Add timeclock entry objects to array
        for row in cursor:
            username = row[0]
            time_in = row[1]
            time_out = row[2]
            dept = job_id_to_dept_dict.get(str(row[3]), "???")
            note = row[4]
            tc_entries.append(TimeclockEntry(username, time_in, time_out,
                                             dept, note))

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
