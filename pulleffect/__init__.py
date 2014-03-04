# -*- coding: utf-8 -*-
"""
    Pull Effect
    ~~~~~~

    An information consolidation machine or something.
"""

from flask import Flask
from flask import render_template
from flask import session
from pulleffect.lib.utilities import mongo_connection
from pulleffect.lib.google.gcal import gcal
from pulleffect.lib.google.gplus import gplus
from pulleffect.lib.utilities import signin_required
from pulleffect.lib.messages.messages import messages

from markupsafe import Markup
import urllib


app = Flask(__name__)
app.register_blueprint(gcal, url_prefix='/gcal')
app.register_blueprint(gplus, url_prefix='/gplus')
app.register_blueprint(messages, url_prefix='/messages')


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


if __name__ == '__main__':
    app.run()
