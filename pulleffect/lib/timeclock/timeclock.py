from flask import Blueprint
from flask import jsonify
from pulleffect.lib.utilities import signin_required
from pulleffect.lib.timeclock.timeclock_entry import TimeclockEntry

timeclock = Blueprint('timeclock', __name__, template_folder='templates')


@timeclock.route('')
@signin_required
def index():
    timeclock_entry = TimeclockEntry.query.filter_by(
        username='aburkart').first()
    print timeclock_entry.time_in
    return jsonify(timeclock_entry)

    # # Open connection to database
    # connection = wes_timeclock_engine.begin()

    # # Get the most recently clocked in employee
    # employees = connection.execute("SELECT * FROM "
    # 	"(SELECT USERNAME, ID, TIME_IN, TIME_OUT FROM ACLC_USDAN.NED_SHIFT"
    # " ORDER BY TIME_IN DESC) "
    # 	"WHERE ROWNUM = 1")

    # for employee in employees:
    # 	print "username", employee["USERNAME"]

    # connection.close()
