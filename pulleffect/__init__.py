# -*- coding: utf-8 -*-
"""
    Pull Effect
    ~~~~~~

    An information consolidation machine or something.
"""

# from sqlite3 import dbapi2 as sqlite3
# from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, json, jsonify, make_response
from flask import Flask
from flask import render_template
from flask import session
from pulleffect.lib.google.gcal import gcal
from pulleffect.lib.google.gplus import gplus
from pulleffect.lib.utilities import signin_required


app = Flask(__name__)
app.register_blueprint(gcal, url_prefix='/gcal')
app.register_blueprint(gplus, url_prefix='/gplus')

# print app.url_map

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE='/tmp/pulleffect.db',
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('PULLEFFECT_SETTINGS', silent=True)


@app.route('/')
def index():
    # db = get_db()
    # cur = db.execute('select title, text from entries order by id desc')
    # entries = cur.fetchall()
    # return render_template('show_entries.html', entries=entries)

    dashboards = mongo_connection.dashboards
    dashboard = dashboards.find_one({}, { "_id": 0 });

    return render_template('index.html', dashboard=dashboard)



if __name__ == '__main__':
    # init_db()
    app.run()
