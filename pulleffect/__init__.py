# -*- coding: utf-8 -*-
"""
    Pull Effect
    ~~~~~~

    An information consolidation machine or something.
"""

from flask import Flask
from flask import render_template
from flask_cas import CAS
from pulleffect.lib.google.gcal import gcal
from pulleffect.lib.google.gplus import gplus
# from pulleffect.lib.notes.notes import notes
from pulleffect.lib.service.service import service
# from pulleffect.lib.timeclock.timeclock import timeclock
from pulleffect.lib.messages.messages import messages
from pulleffect.middleware.reverse_proxy_fix import ReverseProxied
from pulleffect.lib.utilities import cache
from pulleffect.lib.utilities import signin_required
from werkzeug.contrib.fixers import ProxyFix
import pulleffect.config.env as env

app = Flask(__name__)

# Init CAS integration
app.config['CAS_SERVER'] = 'http://sso.wesleyan.edu'
app.config['CAS_AFTER_LOGIN'] = 'index'
CAS(app, '/cas')

# Init function caching
cache.init_app(app, config={'CACHE_TYPE': 'simple'})

# Init blueprints
app.register_blueprint(gcal, url_prefix='/gcal')
app.register_blueprint(gplus, url_prefix='/gplus')
app.register_blueprint(messages, url_prefix='/messages')
# app.register_blueprint(notes, url_prefix='/notes')
app.register_blueprint(service, url_prefix='/service')
# app.register_blueprint(timeclock, url_prefix='/timeclock')

# This is necessary until we get a vagrant box up and running
if not env.is_dev:
    from pulleffect.lib.timeclock.timeclock import timeclock
    app.register_blueprint(timeclock, url_prefix='/timeclock')


# Load default config and override config from an environment variable
app.config.update(dict(
    DEBUG=True,
    SECRET_KEY='development key'
))


@app.route('/')
@signin_required
def index():
    return render_template('index.html')

# Some reverse proxy stuff that was necessary for pulleffect to work as
# a subroute in Rob's nginx setup
app.wsgi_app = ProxyFix(app.wsgi_app)
app.wsgi_app = ReverseProxied(app.wsgi_app)

if __name__ == '__main__':
    app.run()
