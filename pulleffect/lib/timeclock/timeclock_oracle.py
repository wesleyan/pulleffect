import cx_Oracle
from flask import Blueprint
from flask import jsonify
from flask import url_for
from flask import signin_required

timeclock = Blueprint('timeclock', __name__, template_folder='templates')

@timeclock.route('/timeclock')
@signin_required
def timeclock():

try:
	wes_timeclock_connection = cx_Oracle.connect(
		config['wes_timeclock_username'], 
		config['wes_timeclock_password'], 
		config['wes_timeclock_connection_string'])



