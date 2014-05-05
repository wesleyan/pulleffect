from flask import Blueprint
from flask import jsonify
from flask import request
from pulleffect.lib.utilities import signin_required
from pulleffect.lib.utilities import wes_timeclock_pool
from datetime import datetime
import cx_Oracle

timeclock = Blueprint('timeclock', __name__, template_folder='templates')


# Timeclock entry model
class TimeclockEntry:
    def __init__(self, username, time_in, time_out, job_id, note):
        self.username = username
        self.time_in = time_in
        self.time_out = time_out
        # self.role = role
        self.job_id = job_id
        self.note = note

    # Serializes the object into a dictionary so it can be jsonified
    def serialize(self):
        return {
            'username': self.username,
            'time_in': self.time_in,
            'time_out': self.time_out,
            # 'role': self.role,
            'job_id': self.job_id,
            'note': self.note
        }


# Query object
class QueryObject:
    def __init__(self, query, named_params):
        self.query = query
        self.named_params = named_params


# Get the query to execute on the db
def get_query_object(username, time_in, time_out, job_ids):
    # The stuff that probably won't ever change
    select_clause = ("SELECT * FROM (SELECT USERNAME, TIME_IN, TIME_OUT, "
                     "JOB_ID, NOTE FROM ACLC_USDAN.NED_SHIFT ORDER BY "
                     "TIME_IN DESC) ")

    time_in_var = "TO_TIMESTAMP(:time_in,'yyyy-mm-dd hh24.mi.ss.ff')"
    time_out_var = "TO_TIMESTAMP(:time_out,'yyyy-mm-dd hh24.mi.ss.ff')"

    # Edit later if you ever need to tweak the query
    where_clause = ("WHERE TIME_IN >= {0} AND TIME_OUT <= {1} AND "
                    "JOB_ID IN ".format(time_in_var, time_out_var))

    # Named params that fill in the 'where_clause'
    named_params = {'time_in': time_in, 'time_out': time_out}

    job_id_clause = "("
    for i in range(len(job_ids)):
        named_params['job_id' + str(i)] = job_ids[i]
        job_id_clause += ":{0},".format("job_id" + str(i))

    where_clause += job_id_clause[:-1] + ")"

    # Append the username if it was given
    if username is not None:
        where_clause += " AND USERNAME=:username"
        named_params['username'] = username

    # Completed query
    query = "{0}{1}".format(select_clause, where_clause)

    return QueryObject(query, named_params)


@timeclock.route('')
@signin_required
def index():
    # Default query parameters
    now = datetime.today()
    begin_of_month = datetime(now.year, now.month, 1)
    job_ids = ("(272271, 4044, 2832, 28203, 4050, 35696, 4052, 2836, 66847, "
               "24502, 4045, 4046, 4047, 4048, 4049, 308306)")
    job_ids = job_ids[1:-1].split(',')

    # Named parameters for query
    username = request.args.get('username', None)
    time_in = request.args.get('time_in', str(begin_of_month))
    time_out = request.args.get('time_out', str(now))
    job_ids = request.args.get('job_ids', job_ids)

    # Grab connection from pool of connections
    connection = wes_timeclock_pool.acquire()
    try:
        # Get cursor from connection
        cursor = connection.cursor()

        # Get query object
        query_object = get_query_object(username, time_in, time_out, job_ids)

        # Execute query against db
        cursor.execute(query_object.query, query_object.named_params)

        # Build array of timeclock entries retrieved in cursor
        timeclock_entries = []

        # Add timeclock entry objects to array
        for row in cursor:
            timeclock_entries.append(TimeclockEntry(row[0], row[1],
                                                    row[2], row[3]))

        # Serialize array of timeclock entries
        timeclock_entries = [entry.serialize() for entry in timeclock_entries]
        return jsonify(timeclock_entries=timeclock_entries)

    # Catch exceptions that may be thrown during connection to database
    except cx_Oracle.DatabaseError, exception:
        error, = exception
        session_killed = 28
        # Drop the connection if the query fails
        if error.code == session_killed:
            wes_timeclock_pool.drop(connection)
        # Return error
        return jsonify(error=str(error))
    else:
        cursor.close()
        wes_timeclock_pool.release(connection)
        return jsonify(error="not sure what dafuz happened")
