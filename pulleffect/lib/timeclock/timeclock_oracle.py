from flask import Blueprint
from flask import jsonify
from flask import url_for
from flask import signin_required
from pulleffect.config.env import config
from pulleffect.lib.utilities import wes_timeclock_engine

timeclock = Blueprint('timeclock', __name__, template_folder='templates')

@timeclock.route('/timeclock')
@signin_required
def timeclock():
	# Open connection to database
	connection = wes_timeclock_engine.begin()

	# Get the most recently clocked in employee
	employees = connection.execute("SELECT * FROM "
		"(SELECT USERNAME, ID, TIME_IN, TIME_OUT FROM ACLC_USDAN.NED_SHIFT ORDER BY TIME_IN DESC) "
		"WHERE ROWNUM = 1")

	for employee in employees:
		print "username", employee["USERNAME"]

	connection.close()





