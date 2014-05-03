from pymongo import MongoClient
from functools import wraps
from flask import session
from flask import render_template
from pulleffect.config.env import config
from pulleffect.config.env import is_beta
import cx_Oracle

# Mongo database connection
client = MongoClient('localhost', 27017)
mongo_connection = client.pulleffect

# More oracle stuff that will break the dev machines if loaded
if is_beta:
    # Need to be wrapped in str because unicode does not work with Oracle
    wes_timeclock_username = str(config['wes_timeclock_username'])
    wes_timeclock_password = str(config['wes_timeclock_password'])

    # Construct oracle dsn
    wes_timeclock_dsn = cx_Oracle.makedsn(host='curltest.db.wesleyan.edu',
                                          port=2111,
                                          service_name='CURLTEST.WESLEYAN.EDU')

    # Construct oracle database connection pool
    wes_timeclock_pool = cx_Oracle.SessionPool(wes_timeclock_username,
                                               wes_timeclock_password,
                                               wes_timeclock_dsn, 1, 4, 1)

# Single point of reference for database names
db_names = {
    "wes_timeclock": "wes_timeclock"
}


# Middleware to ensure user is authenticated before accessing a route
# Just stick @signin_required above any route method calls
def signin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('signed_in'):
            return render_template('signin.html')
        return f(*args, **kwargs)
    return decorated_function
