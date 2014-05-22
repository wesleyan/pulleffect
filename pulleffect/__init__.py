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

import json
import logging
from flask import Flask
from flask import render_template
import pulleffect.config.env as env
from pulleffect.lib.flask_cas import CAS
from pulleffect.lib.messages.messages import messages
from pulleffect.lib.notes.notes import notes
from pulleffect.lib.service.service import service
from pulleffect.lib.utilities import cache
from pulleffect.lib.utilities import require_signin
from pulleffect.lib.utilities import configure_logging
from pulleffect.middleware.reverse_proxy_fix import ReverseProxied
from werkzeug.contrib.fixers import ProxyFix

app = Flask(__name__)

# Init CAS integration
app.config['CAS_SERVER'] = env.config["cas_server"]
app.config['CAS_AFTER_LOGIN'] = env.config["cas_route_after_login"]
app.config['CAS_LOGIN_ROUTE'] = env.config["cas_server_login_route"]
app.config['CAS_LOGOUT_ROUTE'] = env.config["cas_server_logout_route"]
app.config['CAS_VALIDATE_ROUTE'] = env.config["cas_server_validate_route"]
CAS(app)

# Init function caching
cache.init_app(app, config={'CACHE_TYPE': 'simple'})

# Configure logging
configure_logging()

# Init blueprints
app.register_blueprint(messages, url_prefix='/messages')
app.register_blueprint(notes, url_prefix='/notes')
app.register_blueprint(service, url_prefix='/service')
# app.register_blueprint(timeclock, url_prefix='/timeclock')

# Stops Pulleffect from breaking when run without google client secrets
try:
    json.load(open(env.config["google_client_secrets"]))
    from pulleffect.lib.google.gcal import gcal
    app.register_blueprint(gcal, url_prefix='/gcal')
except IOError as e:
    logging.warning("You need to include a google_client_secrets.json file in"
                    "the  pulleffect/config/ directory")

# This is necessary when you're not working on a vagrant box
if not env.is_dev:
    from pulleffect.lib.timeclock.timeclock import timeclock
    app.register_blueprint(timeclock, url_prefix='/timeclock')

# TODO(arthurb): The secret key needs to be changed
app.config.update(dict(
    DEBUG=env.is_dev,
    SECRET_KEY='development key'
))


@app.route('/')
@require_signin
def index():
    return render_template('index.html')

# Some reverse proxy stuff that was necessary for pulleffect to work as
# a subroute in Rob's nginx setup
app.wsgi_app = ProxyFix(app.wsgi_app)
app.wsgi_app = ReverseProxied(app.wsgi_app)

if __name__ == '__main__':
    app.run()
