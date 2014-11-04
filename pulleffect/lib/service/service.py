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
import logging
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
import mechanize
import httplib2
import urllib2
import os
import pymongo
import requests
import strict_rfc3339
import base64
from SOAPpy import SOAPProxy

service = Blueprint('service', __name__, template_folder='templates')


@service.route('/records')
def records():
    test = {'here': 'here'}
    username = "ims1"
    password = quote_plus("service@now!")
    url = "https://wesleyanedu.service-now.com/incident.do?JSON&sysparm_action=getRecords&sysparm_query=active=false"
    # url = "http://" + username + ":" + password + "@" + urlpath

    br = mechanize.Browser()
    br.set_handle_robots(False)
    br.addheaders.append(('Authorization', 'Basic %s' % base64.encodestring('%s:%s' % (username, "service@now!"))))   
    x = br.open(url)
    records = json.loads(x.read())
    return jsonify(records)





    # br.form = list(br.forms())[0]
    # br["username"] = "ims1"
    # br["password"] = "service@now!"    
    # request = br.submit()

    # logging.info(request.read())


    # br.select_form(name="fm1")

    # br.submit()





    # password = quote_plus("service@now!")
    # urlpath = "wesleyanedu.service-now.com/incident.do?JSON$sysparm_action=getRecords"
    # url = "http://" + username + ":" + password + "@" + urlpath
    # browser = webdriver.Firefox()
    # browser.get(url)
    # userfield = browser.find_element_by_name("username")
    # userfield.send_keys(username)
    # passfield = browser.find_element_by_name("password")
    # passfield.send_keys("service@now!")
    # logging.info(passfield.send_keys(Keys.RETURN))
    # logging.info("****")




    # username, password, instance = 'ims1', 'service@now!', 'wesleyanedu'
    # proxy = 'https://%s:%s@www.service-now.com/%s/incident.do?SOAP'%(username,password,instance)
    # namespace = 'http://www.service-now.com/'
	 
    # server = SOAPProxy(proxy,namespace)
    # logging.info(server)
    # response = server.getRecords()
	 
 #    for record in response:
 #        for item in record:
 #    	   print item
    return jsonify(test)
