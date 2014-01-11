from flask import Blueprint, flash, jsonify, redirect, request, session, url_for
from pulleffect.lib.utilities import signin_required

user = Blueprint('user', __name__, template_folder='templates')

# Sign in user
@user.route('/signin', methods=['POST'])
def signin():
    if request.json['u'] != 'admin' or request.json['p'] != 'default':
        return jsonify({'alert':[['error', 'Invalid username or password.']]})
    session['signed_in'] = True 
    flash('Successfully signed in', 'success')
    return jsonify({'redirect':url_for('index')})

# Sign out user
@user.route('/signout', methods=['POST'])
@signin_required
def signout():
    session.pop('signed_in', None)
    flash('You are signed out.', 'success')
    return redirect(url_for('index'))