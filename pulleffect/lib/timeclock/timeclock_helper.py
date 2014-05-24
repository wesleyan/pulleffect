import cx_Oracle
import pulleffect.lib.timeclock.timeclock_objects as tc_obj
import pulleffect.lib.timeclock.timeclock_depts as tc_depts
from pulleffect.lib.utilities import wes_timeclock_pool


def build_timeclock_entries(cursor):
    """Build TimeclockEntry from cursor

    Keyword arguments:
        cursor -- tuple representation of Oracle SQL query results

    Returns:
        array -- An array containing TimeclockEntry objects
    """
    # Add timeclock entry objects to array
    tc_entries = [
        tc_obj.TimeclockEntry(
            row[0], row[1], row[2],
            tc_depts.get_dept(str(row[3]), "???"),
            row[4])
        for row in cursor
    ]
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
    # try-except-else statements and fix.
    else:
        cursor.close()
        wes_timeclock_pool.release(connection)
        return {'error': 'not sure what dafuz happened'}
