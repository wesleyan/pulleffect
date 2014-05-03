from pymongo import MongoClient
from functools import wraps
from flask import session
from flask import render_template
from pulleffect.config.env import config
import cx_Oracle

# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker

# Mongo database connection
client = MongoClient('localhost', 27017)
mongo_connection = client.pulleffect

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
# Timeout for connection
# wes_timeclock_pool.timeout = 50

# Wes timeclock database connection
# wes_timeclock_engine = create_engine('oracle://{0}:{1}@{2}'.format(
#     config['wes_timeclock_username'],
#     config['wes_timeclock_password'],
#     config['wes_timeclock_connection_string']), echo=True)

# sqla_session = sessionmaker(bind=wes_timeclock_engine)

# This dictionary contains all the database names
# that we use, so if we ever name them something different,
# we can just change the name in one spot
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
