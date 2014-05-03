from flask import Blueprint
from flask import jsonify
from pulleffect.lib.utilities import signin_required
from pulleffect.lib.utilities import wes_timeclock_pool
import cx_Oracle

timeclock = Blueprint('timeclock', __name__, template_folder='templates')


# Tiemclock entry model
class TimeclockEntry:
    def __init__(self, username, time_in, time_out):
        self.username = username
        self.time_in = time_in
        self.time_out = time_out

    # Serializes the object into a dictionary so it can be jsonified
    def serialize(self):
        return {
            'username': self.username,
            'time_in': self.time_in,
            'time_out': self.time_out
        }


@timeclock.route('')
@signin_required
def index():
    # Grab connection from pool of connections
    connection = wes_timeclock_pool.acquire()
    try:
        # Get cursor from connection
        cursor = connection.cursor()

        # Make a query to the database
        # TODO(arthurb): This will need to be abstracted in order to
        # accomodate all the different queries we may make to this route
        cursor.execute("SELECT * FROM (SELECT USERNAME, TIME_IN,"
                       " TIME_OUT FROM ACLC_USDAN.NED_SHIFT ORDER BY "
                       "TIME_IN DESC) WHERE ROWNUM <= 20")

        # Build array of timeclock entries retrieved in cursor
        timeclock_entries = []
        for row in cursor:
            # Add timeclock entry objects to array
            timeclock_entries.append(TimeclockEntry(row[0], row[1], row[2]))

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
