from apiclient.discovery import build
from flask import Blueprint
from flask import jsonify
from flask import json
from flask import redirect
from flask import request
from flask import session
from flask import url_for
from markupsafe import Markup
from oauth2client.client import flow_from_clientsecrets
from pulleffect.lib.utilities import mongo_connection
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from urllib import urlencode
from urllib import quote_plus
import httplib2
import os
import pymongo
import requests
import strict_rfc3339

service = Blueprint('service', __name__, template_folder='templates')


@service.route('/records')
def records():
    # test = {'here': 'here'}
    # username = "ims1"
    # password = quote_plus("")
    # urlpath = "wesleyanedu.service-now.com/incident.do?JSON$sysparm_action=getRecords"
    # url = "http://" + username + ":" + password + "@" + urlpath
    # browser = webdriver.Firefox()
    # browser.get(url)
    # return jsonify(test)
    return
