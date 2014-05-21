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
