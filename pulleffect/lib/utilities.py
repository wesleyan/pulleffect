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
import logging

# Get db configs to initiate db connections
db_configs = env.config['databases']


def represents_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def configure_logging():
    """Configures logging for application.

        Usage:
            For every file where you want to use logging, just
            `import logging` and use it like `logging.info('hello')`
    """
    # Set up logging to a file
    logging.basicConfig(
        filename='pulleffect.log', level=logging.DEBUG,
        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        filemode='w')

    # Set up logging to the console
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)

    # Attach the console logger to the default logger
    logging.getLogger('').addHandler(console)


def require_signin(f):
    """Middleware forces users to sign in whenever they make a request
        to a private route controller.

    Args:
        f -- this is the function that is being wrapped by require_signin

    Example usage:
        @require_signin
        def function_name():
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Build email for connected user
        email = "@{0}".format(env.config["organization_email"])

        # Force users to log in when in production
        if not env.is_dev:
            username = session.get(
                current_app.config['CAS_USERNAME_SESSION_KEY'], None)

            if not username:
                return redirect('/login')

            # Build email for username
            email = "{0}{1}".format(username, email)

            # Get user with username
            user = mongo_connection.users.find_one({"username": username})

            # If user doesn't exist in database, insert new user
            if not user:
                mongo_connection.users.insert({
                    "username": username,
                    "email": email
                })
        # Log in dummy user when in development
        else:
            username = "dummy"
            email = "{0}{1}".format(username, email)

            # # If user doesn't exist in database, insert new user
            user = mongo_connection.users.find({"username": username})
            if not user:
                mongo_connection.users.insert({
                    "username": username,
                    "email": email
                })

        session["username"] = username
        session["email"] = email
        session["signed_in"] = True
        return f(*args, **kwargs)
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
        db_username = str(db_config['username'])
        db_password = str(db_config['password'])

        # Build DSN
        dsn_config = db_config['dsn']
        db_dsn = cx_Oracle.makedsn(
            host=str(dsn_config['host']),
            port=str(dsn_config['port']),
            service_name=str(dsn_config['service_name']))

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
