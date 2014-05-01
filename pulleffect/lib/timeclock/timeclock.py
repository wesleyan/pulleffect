from flask import Blueprint
from flask import jsonify
from flask import url_for
from datetime import datetime, timedelta
from pulleffect.config.env import config
from pulleffect.lib.timeclock.timeclock_models import TimeclockEntry
from pulleffect.lib.utilities import signin_required

timeclock = Blueprint('timeclock', __name__, template_folder='templates')

@timeclock.route('')
@signin_required
def index():
	# TimeclockEntry.query.filter((TimeclockEntry.time_out == None)
	# 	|| (TimeclockEntry.time_in > datetime.today() - timedelta(hours=5)))

	# Grab the ten most recently clocked in workers
	timeclock_entries = TimeclockEntry.query.order_by(TimeclockEntry.time_in).limit(10)

	for timeclock_entry in timeclock_entries:
		print timeclock_entry
	# # Open connection to database
	# connection = wes_timeclock_engine.begin()

	# # Get the most recently clocked in employee
	# employees = connection.execute("SELECT * FROM "
	# 	"(SELECT USERNAME, ID, TIME_IN, TIME_OUT FROM ACLC_USDAN.NED_SHIFT ORDER BY TIME_IN DESC) "
	# 	"WHERE ROWNUM = 1")

	# for employee in employees:
	# 	print "username", employee["USERNAME"]

	# connection.close()





