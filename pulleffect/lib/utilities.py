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
from flask import flash
from pymongo import MongoClient
from flask.ext.cache import Cache
import pulleffect.config.env as env
import cx_Oracle
import logging

# Get db configs to initiate db connections
db_configs = env.config['databases']


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
        # Check if user is signed in
        signed_in = session.get('signed_in', False)
        if not signed_in:
            username = env.config['sys_user'] if env.is_dev else session.get(
                current_app.config['CAS_USERNAME_SESSION_KEY'], None)

            if not username:
                return redirect('/login')

           # Build email for connected user
            email = "{0}@{1}".format(
                    username,
                    env.config["organization_email"])

            # If user has never logged in before, add them to database
            user = mongo_connection.users.find_one({"username": username})

            # If user doesn't exist in database, insert new user
            if not user:
                # Add user to database
                mongo_connection.users.insert({
                    "username": username,
                    "email": email
                })

            # Sign in the connected user
            session['username'] = username
            session['email'] = email
            session['signed_in'] = True
            flash("Welcome {0}".format(username), "success")
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


def enum(*sequential, **named):
    """Support for enums in Python 2.7.

        Keyword arguments:
            sequential -- TODO(arthurb): I don't really get it
            named -- TODO(arthurb): I don't really get it

        Code found on SO: bit.ly/1r13fHs

        Example:
            >>> Colors = enum('RED', 'BLUE', 'GREEN')
            >>> Colors.RED
            0
            >>> Colors.reverse_mapping.get(0)
            RED
    """
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)

# Oracle stuff that will 'break' dev machines if loaded
if not env.is_dev:
    # Build pooled Oracle database connection for Wesleyan timeclock
    wes_timeclock_config = db_configs['wes_timeclock']
    wes_timeclock_pool = build_db_connection(wes_timeclock_config, "oracle")
if env.is_dev:
    wes_timeclock_pool = None
# Mongo database connection
mongo_connection = build_db_connection(db_configs['local_mongo'], 'mongo')

# Used for caching function calls
cache = Cache()

Widgets = enum('GCAL', 'MESSAGES', 'NOTES', 'SERVICE', 'TIMECLOCK', 'SHIFTS')
