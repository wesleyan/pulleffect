from pymongo import MongoClient
from functools import wraps
from flask import session
from flask import render_template

client = MongoClient('localhost', 27017)
mongo_connection = client.pulleffect

def signin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('signed_in'):
            return render_template('signin.html')
        return f(*args, **kwargs)
    return decorated_function