# Copyright (C) 2014 Wesleyan University
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from functools import wraps
from flask import session
from flask import redirect
from flask import current_app
from pymongo import MongoClient
from flask.ext.cache import Cache
import pulleffect.config.env as env
import cx_Oracle

# Get db configs to initiate db connections
db_configs = env.config['databases']


def signin_required(f):
    """Middleware to ensure user is authenticated before accessing a route.
    Just stick @signin_required above any route method calls

    Args:
        f -- this is the function that is being wrapped by signin_required

    Example usage:
        @signin_required
        def function_name():
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Automatically sign in if in dev-mode
        if env.is_dev:
            session['signed_in'] = True
            return f(*args, **kwargs)
        # Otherwise force them through the CAS
        else:
            username = session.get(
                current_app.config['CAS_USERNAME_SESSION_KEY'], None)
            if not username:
                return redirect('/login')
    return decorated_function


def build_db_connection(db_config, db_type):
    """Shove a database configuration into this function
       to build a connection to it.

       Args:
            db_config -- a configuration of the form:

                "wes_timeclock": {
                    "username": "student_timeclock",
                    "password": "",
                    "dsn": {
                        "host": "curltest.db.wesleyan.edu",
                        "port": 2111,
                        "service_name": "CURLTEST.WESLEYAN.EDU"
                    }
                }

            db_type -- a very simple way of indicating the
                       database connection type to build
    """
    # Oracle connections
    if db_type is "oracle":
        # Get username and password
        db_username = db_config['username']
        db_password = db_config['password']

        # Build DSN
        dsn_config = db_config['dsn']
        db_dsn = cx_Oracle.makedsn(host=dsn_config['host'],
                                   port=dsn_config['port'],
                                   service_name=dsn_config['service_name'])
        # Return Oracle connection
        return cx_Oracle.SessionPool(db_username, db_password, db_dsn, 1, 4, 1)

    # Mongo connections
    elif db_type is "mongo":
        dsn_config = db_config['dsn']
        client = MongoClient(dsn_config['host'], dsn_config['port'])
        return client.pulleffect
    else:
        return

# Oracle stuff that will 'break' dev machines if loaded
if not env.is_dev:
    # Build pooled Oracle database connection for Wesleyan timeclock
    wes_timeclock_config = db_configs['wes_timeclock']
    wes_timeclock_pool = build_db_connection(wes_timeclock_config, "oracle")

# Mongo database connection
mongo_connection = build_db_connection(db_configs['local_mongo'], 'mongo')

# Used for caching function calls
cache = Cache()
