from pymongo import MongoClient
from functools import wraps
from flask import session
from flask import render_template
# from pulleffect.config.env import config
# from sqlalchemy import create_engine

# Mongo database connection
client = MongoClient('localhost', 27017)
mongo_connection = client.pulleffect

# Wes timeclock database connection
# wes_timeclock_engine = create_engine('oracle://{0}:{1}@{2}'.format(
#     config['wes_timeclock_username'],
#     config['wes_timeclock_password'],
#     config['wes_timeclock_connection_string']))

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
