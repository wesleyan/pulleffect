
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


class TestCases(unittest.TestCase):

    def setUp(self):
        """Before each test, set up a blank database

        """
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
    def test_authenticate_gcal(self, mock_get_google_auth_uri_from_username):
        mock_get_google_auth_uri_from_username.return_value = 'correct.uri'
        rv = self.app.get('/gcal/authenticate')
        assert b'correct.uri' in rv.data

    @patch('pulleffect.lib.google.gcal_helper.try_validate_google_authorization_code')
    def test_oauth2_callback_gcal(self, mock_try_validate_google_authorization_code):
        mock_try_validate_google_authorization_code.return_value = 'validation works!'
        rv = self.app.get('/gcal/oauth2callback')
        assert b'redirect' in rv.data

    @patch('pulleffect.lib.google.gcal_helper.get_calendar_list')
    def test_calendar_list_gcal(self, mock_get_calendar_list):
        mock_get_calendar_list.return_value = {'calendar': 'list of items'}
        rv = self.app.get('/gcal/calendar_list')
        assert b'list of items'in rv.data
    @patch('pulleffect.lib.google.gcal_helper.get_calendar_events')    
    def test_calendar_events_gcal(self,mocked_get_calendar_events):
        params = json.dumps({
            "id": "3dfsljkertwu",
            "now": "12:30:12"
            })
        flask.session["username"] = "dog"
        mocked_get_calendar_events.return_value = {"item":"event_data", "desc": "terrible client","item2":"event2", "desc": "tony the tiger"}
        rv = self.app.get('/gcal/calendar_events',data = params,content_type = 'application/json')
        assert b'event_data' in rv.data

if __name__ == '__main__':
    unittest.main()
