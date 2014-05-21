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


# -*- coding: utf-8 -*-
"""
    Pull Effect
    ~~~~~~

    An information consolidation machine or something.
"""

from flask import Flask
from flask import render_template
from pulleffect.lib.flask_cas import CAS
from pulleffect.lib.notes.notes import notes
from pulleffect.lib.service.service import service
# from pulleffect.lib.timeclock.timeclock import timeclock
from pulleffect.lib.messages.messages import messages
from pulleffect.middleware.reverse_proxy_fix import ReverseProxied
from pulleffect.lib.utilities import cache
from pulleffect.lib.utilities import signin_required
from werkzeug.contrib.fixers import ProxyFix
import pulleffect.config.env as env
import json


app = Flask(__name__)

# Init CAS integration
app.config['CAS_SERVER'] = 'https://sso.wesleyan.edu'
app.config['CAS_AFTER_LOGIN'] = 'index'
app.config['CAS_LOGIN_ROUTE'] = '/login'
app.config['CAS_LOGOUT_ROUTE'] = '/logout'
app.config['CAS_VALIDATE_ROUTE'] = '/validate'
CAS(app)

# Init function caching
cache.init_app(app, config={'CACHE_TYPE': 'simple'})

# Init blueprints
app.register_blueprint(messages, url_prefix='/messages')
app.register_blueprint(notes, url_prefix='/notes')
app.register_blueprint(service, url_prefix='/service')
# app.register_blueprint(timeclock, url_prefix='/timeclock')

# Prevents Pulleffect from breaking down when you run it
# without google client secrets
try:
    json.load(open(env.config["google_client_secrets"]))
    from pulleffect.lib.google.gcal import gcal
    app.register_blueprint(gcal, url_prefix='/gcal')
# TODO(arthurb): This is dumb, logging should be better than this
except IOError as e:
    print ("ERROR:\nYou need to include a google_client_secrets.json "
           "file in your pulleffect/config/ directory.")

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
