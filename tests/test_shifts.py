import os
import pulleffect
import unittest
import tempfile
import json
import flask
import requests
from mock import patch
from mock import MagicMock
import pulleffect.lib.timeclock
from pulleffect.lib.utilities import Widgets
import logging
#does not test try_get_timeclock_entries as it relies completely on oracle
class TestCases(unittest.TestCase):

	def setUp(self):
		"""Before each test, set up a blank database"""
		self.db_fd, pulleffect.app.config['DATABASE'] = tempfile.mkstemp()
		pulleffect.app.config['TESTING'] = True
		self.app = pulleffect.app.test_client()
		self.ctx = pulleffect.app.test_request_context()
		self.ctx.push()
	def tearDown(self):
		"""Get rid of the database again after each test."""
		os.close(self.db_fd)
		os.unlink(pulleffect.app.config['DATABASE'])
		self.ctx.pop()

	@patch('pulleffect.lib.google.gcal_helper.get_google_auth_uri_from_username')
	def test_authenticate_shifts(self,mock_get_google_auth_uri_from_username):
	    mock_get_google_auth_uri_from_username.return_value = 'correct.uri'
	    rv = self.app.get('/shifts/authenticate')
	    assert b'correct.uri' in rv.data

	@patch('pulleffect.lib.google.gcal_helper.try_validate_google_authorization_code')
	def test_oauth2_callback_shifts(self, mock_try_validate_google_authorization_code):
	    mock_try_validate_google_authorization_code.return_value = 'validation works!'
	    rv = self.app.get('/shifts/oauth2callback')
	    assert b'redirect' in rv.data

	@patch('pulleffect.lib.google.gcal_helper.get_calendar_list')
	def test_calendar_list_shifts(self,mock_get_calendar_list):
	    mock_get_calendar_list.return_value = rtn = {'calendar': 'list of items'}
	    rv = self.app.get('/shifts/calendar_list')
	    assert b'list of items'in rv.data
	

	@patch('pulleffect.lib.google.gcal_helper.get_calendar_events')
	def test_shifts_index_redirects(self,mocked_get_calendar_events):
		mocked_get_calendar_events.return_value = { 'redirect':'/shifts/google'}
		rv = self.app.get('/shifts?id=tharden120')
		assert b'redirect' in rv.data

	@patch("pulleffect.lib.timeclock.timeclock_helper.try_get_timeclock_entries")
	@patch("pulleffect.lib.timeclock.timeclock_objects.TimeclockOracleQuery_construct")
	@patch('pulleffect.lib.google.gcal_helper.get_calendar_events')
	def test_shifts_index_(self,mocked_get_calendar_events,mocked_TimeclockOracleQuery_construct,mocked_try_get_timeclock_entries):
		rtn_val  = {}
		rtn_val['items'] = [{'description':'this is an event','start':{'dateTime':'1200'},'end': {'dateTime':'1240'}},
							{'description':'event2','start':{'dateTime':'1452'},'end': {'dateTime':'2000'}}]
		mocked_get_calendar_events.return_value = rtn_val
		rtn_val  = {}
		rtn_val['timeclock_entries'] = 	[{'event':'dog days of summer', 'note':'who let the dogs out?','time_in':'2300','dept': '(events)'}]	
		mocked_try_get_timeclock_entries.return_value = rtn_val
		mocked_TimeclockOracleQuery_construct.return_value = "dog"
		flask.session['sys_user'] = 'tharden'
		rv = self.app.get('/shifts?id=tharden120')
		assert b'dog' in rv.data


if __name__ == '__main__':
    unittest.main()