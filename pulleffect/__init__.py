# -*- coding: utf-8 -*-
"""
    Pull Effect
    ~~~~~~

    An information consolidation machine or something.
"""

from flask import Flask
from flask import render_template
from flask import session
from pulleffect.config.env import config
from pulleffect.lib.utilities import mongo_connection
from pulleffect.lib.google.gcal import gcal
from pulleffect.lib.google.gplus import gplus
from pulleffect.lib.notes.notes import notes
# from pulleffect.lib.timeclock.timeclock import timeclock
from pulleffect.lib.utilities import signin_required
from pulleffect.lib.messages.messages import messages
from pulleffect.lib.cache import cache
from pulleffect.lib.sqlalchemy import db
from pulleffect.middleware.reverse_proxy_fix import ReverseProxied
from markupsafe import Markup
from werkzeug.contrib.fixers import ProxyFix
import urllib


app = Flask(__name__)

# Define database
# SQLALCHEMY_BINDS = {
#     # SQLAlchemy connection string for wes timeclock db
#     'wes_timeclock': 'oracle://{0}:{1}@{2}'.format(
#         config['wes_timeclock_username'],
#         config['wes_timeclock_password'],
#         config['wes_timeclock_connection_string'])
# }
# app.config['SQLALCHEMY_BINDS'] = SQLALCHEMY_BINDS

# Create database connection to wes timeclock database
db.init_app(app)

# Init caching
cache.init_app(app, config={'CACHE_TYPE':'simple'})

# Init blueprints
app.register_blueprint(gcal, url_prefix='/gcal')
app.register_blueprint(gplus, url_prefix='/gplus')
app.register_blueprint(messages, url_prefix='/messages')
app.register_blueprint(notes, url_prefix='/notes')
# app.register_blueprint(timeclock, url_prefix='/timeclock')


# Load default config and override config from an environment variable
app.config.update(dict(
    DEBUG=True,
    SECRET_KEY='development key'
))
app.config.from_envvar('PULLEFFECT_SETTINGS', silent=True)


@app.route('/')
def index():
    dashboards = mongo_connection.dashboards
    dashboard = dashboards.find_one({}, { "_id": 0 });

    return render_template('index.html', dashboard=dashboard)


@app.template_filter('urlencode')
def urlencode_filter(s):
    if type(s) == 'Markup':
        s = s.unescape()
    s = s.encode('utf8')
    s = urllib.quote_plus(s)
    return Markup(s)

app.wsgi_app = ProxyFix(app.wsgi_app)
app.wsgi_app = ReverseProxied(app.wsgi_app);

if __name__ == '__main__':
    app.run()
