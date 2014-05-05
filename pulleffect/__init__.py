    # -*- coding: utf-8 -*-
"""
    Pull Effect
    ~~~~~~

    An information consolidation machine or something.
"""

from flask import Flask
from flask import render_template
from pulleffect.lib.google.gcal import gcal
from pulleffect.lib.google.gplus import gplus
from pulleffect.lib.notes.notes import notes
from pulleffect.lib.service.service import service
# from pulleffect.lib.timeclock.timeclock import timeclock
from pulleffect.lib.messages.messages import messages
from pulleffect.lib.cache import cache
from pulleffect.middleware.reverse_proxy_fix import ReverseProxied
from markupsafe import Markup
from werkzeug.contrib.fixers import ProxyFix
from pulleffect.config.env import is_beta
import urllib

app = Flask(__name__)

# Init caching
cache.init_app(app, config={'CACHE_TYPE': 'simple'})

# Init blueprints
app.register_blueprint(gcal, url_prefix='/gcal')
app.register_blueprint(gplus, url_prefix='/gplus')
app.register_blueprint(messages, url_prefix='/messages')
app.register_blueprint(notes, url_prefix='/notes')
app.register_blueprint(service, url_prefix='/service')
# app.register_blueprint(timeclock, url_prefix='/timeclock')

# The timeclock route depends on Oracle being installed on the machine,
# which is a total pain in the ass to install, so it's ignored on all
# machines but the beta machine
if is_beta:
    from pulleffect.lib.timeclock.timeclock import timeclock
    app.register_blueprint(timeclock, url_prefix='/timeclock')


# Load default config and override config from an environment variable
app.config.update(dict(
    DEBUG=True,
    SECRET_KEY='development key'
))
app.config.from_envvar('PULLEFFECT_SETTINGS', silent=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.template_filter('urlencode')
def urlencode_filter(s):
    if type(s) == 'Markup':
        s = s.unescape()
    s = s.encode('utf8')
    s = urllib.quote_plus(s)
    return Markup(s)

# Some reverse proxy stuff that was necessary for pulleffect to work as
# a subroute in Rob's nginx setup
app.wsgi_app = ProxyFix(app.wsgi_app)
app.wsgi_app = ReverseProxied(app.wsgi_app)

if __name__ == '__main__':
    app.run()
