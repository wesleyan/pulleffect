import os
import pulleffect
import unittest
import tempfile
import json
import flask
from mock import patch
from mock import MagicMock
from pulleffect.lib.utilities import Widgets
import logging

#make unit tests for timeclock, shifts, timeclock_helper, service



"""test file does not test methods that solely rely on the GOOGLE API, 
    as these methods can be assumed to work. These methods include 
    get_gcal_service_from_credentials, google_events_from_service, google_get_session_username
    exchange_code_for_credentials,google_info_update, google_get_user
    is_valid_gcal_access_token,get_gcal_service
"""
gcal_helper = pulleffect.lib.google.gcal_helper


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

    """this is the begining of gcal_helper test cases"""

    @patch('pulleffect.lib.google.gcal_helper.validate_and_refresh_creds')
    @patch('pulleffect.lib.google.gcal_helper.get_google_creds')
    def test_get_calendar_list_for_gcalhelper_without_credentials(self, mocked_get_google_creds, mocked_validate_and_refresh_creds):
        rtn = {"redirect": "/gcal/authenticate"}   
        mocked_validate_and_refresh_creds.return_value = rtn
        mocked_get_google_creds.return_value = 'redirect'
        credentials = gcal_helper.get_calendar_list("name", "widget")
        assert b'redirect' in credentials
    
    @patch('pulleffect.lib.google.gcal_helper.validate_and_refresh_creds')
    @patch('pulleffect.lib.google.gcal_helper.get_gcal_service_from_credentials')
    @patch('pulleffect.lib.google.gcal_helper.get_google_creds')
    @patch('pulleffect.lib.google.gcal_helper.get_gcal_from_service')
    def test_get_calendar_list_for_gcalhelper(self, mocked_get_gcal_from_service, mocked_get_google_creds, mocked_get_gcal_service_from_credentials , mocked_validate_and_refresh_creds):
        """should be failing currently"""
        rtn = {"correct": "creds"}
        rtn_cal = [ {"summary": "this event is in the scwc", "id":4850275},
                    {"summary": "we need more engineers", "id":90324},
                    {"summary": "very IMPORTANT video recording", "id":1037603}
                  ]
        google_creds = {'google':'creds'}
        
        mocked_validate_and_refresh_creds.return_value = rtn
        mocked_get_gcal_service_from_credentials.return_value = 'service_object'
        mocked_get_google_creds.return_value = google_creds
        mocked_get_gcal_from_service.return_value = rtn_cal
        calendar_list = gcal_helper.get_calendar_list("name", "widget")
        assert b'calendar_list' in calendar_list

    @patch('pulleffect.lib.google.gcal_helper.validate_and_refresh_creds')
    @patch('pulleffect.lib.google.gcal_helper.get_google_creds') 
    def test_get_calendar_events_no_creds(self,mocked_get_google_creds,mocked_validate_and_refresh_creds):
        rtn = {"redirect": "/gcal/authenticate"}
        mocked_validate_and_refresh_creds.return_value = rtn
        mocked_get_google_creds.return_value = 'creds'
        rv = gcal_helper.get_calendar_events(
            123512, 1200, 1500, "name", "widget")
        assert b'redirect' in rv

    @patch('pulleffect.lib.google.gcal_helper.get_google_creds')
    @patch('pulleffect.lib.google.gcal_helper.validate_and_refresh_creds')
    @patch('pulleffect.lib.google.gcal_helper.set_google_creds')
    @patch('pulleffect.lib.google.gcal_helper.get_gcal_service_from_credentials')
    @patch('pulleffect.lib.google.gcal_helper.google_events_from_service')
    def test_get_calendar_events(self,mocked_google_events_from_service, mocked_get_gcal_service_from_credentials,mocked_set_google_creds,mocked_validate_and_refresh_creds,mocked_get_google_creds):
        mocked_get_gcal_service_from_credentials.return_value = 'service_object'
        mocked_get_google_creds.return_value = {"correct": "creds"}
        mocked_validate_and_refresh_creds.return_value = {"validated": "google_creds"}
        mocked_set_google_creds.return_value = "Submitted credentials correct" 
        mocked_google_events_from_service.return_value = 'events_correct_if_creds_correct'
        rv = gcal_helper.get_calendar_events('1342349783','13:00','17:00','tharden', 'calendar')
        assert b'events_correct_if_creds_correct' in rv

    @patch('pulleffect.lib.google.gcal_helper.exchange_code_for_credentials')
    @patch('pulleffect.lib.google.gcal_helper.google_get_session_username')
    @patch('pulleffect.lib.google.gcal_helper.get_refresh_token_from_username')
    @patch('pulleffect.lib.google.gcal_helper.set_google_creds')
    @patch('pulleffect.lib.google.gcal_helper.google_info_update')
    def test_try_validate_google_authorization_code(self,mocked_google_info_update,mocked_set_google_creds, mocked_get_refresh_token_from_username, mocked_google_get_session_username, mocked_exchange_code_for_credentials):

        mocked_exchange_code_for_credentials.return_value = {"access_token": "google_access_token"}
        mocked_google_get_session_username.return_value = "username"
        mocked_google_info_update.return_value = "system changes complete"
        mocked_get_refresh_token_from_username.return_value= {'refreshed_access_token': 'c1234nksd9231'}
        rv = gcal_helper.try_validate_google_authorization_code('t7bc389ads', "widget")
        self.assertEqual(True,rv)

    def test_try_validate_google_authorization_without_code(self):
        rv = gcal_helper.try_validate_google_authorization_code('', "widget")
        self.assertEqual(False,rv)
    
    def test_set_google_creds_when_widgits_is_shifts(self):
        gcal_helper.set_google_creds("tharden", 'credentials', Widgets.SHIFTS)
        assert b'credentials' in flask.session['sys_google_creds']
    
    def test_set_google_creds_for_all_widgets_but_shifts(self):   
        gcal_helper.set_google_creds("tharden", 'credentials', '')
        assert b'credentials' in flask.session['google_creds']

    @patch("pulleffect.lib.google.gcal_helper.is_valid_gcal_access_token")
    def test_get_gcal_access_token_with_valid_token(self, mocked_is_valid_gcal_access_token):
        mocked_is_valid_gcal_access_token.return_value = True
        i = { "access_token": "correct_access_token"}
        rv = gcal_helper.get_gcal_access_token(i)
        assert b'correct_access_token' in rv
    @patch('pulleffect.lib.google.gcal_helper.get_refresh_token_from_username')
    @patch('pulleffect.lib.google.gcal_helper.refresh_gcal_access_token')
    def test_get_get_gcal_access_token_invalid_token(self, mocked_refresh_gcal_access_token, mocked_get_refresh_token_from_username):
        i = { "access_token": ""}
        flask.session['username'] = 'tom_the_tester'
        mocked_refresh_gcal_access_token.return_value = 'correct_access_token'
        mocked_get_refresh_token_from_username.return_value = 'I\'m feeling refreshed!'
        rv = gcal_helper.get_gcal_access_token(i)
        assert b'correct_access_token' in rv

    def test_validate_and_refresh_without_creds(self):
        creds = None
        rv = pulleffect.lib.google.gcal_helper.validate_and_refresh_creds(creds)
        assert b'redirect' in rv

    def test_validate_and_refresh_creds_with_bad_token(self):
         creds = "creds"
         initial_credientials = {}
         gcal_helper.get_access_token = MagicMock(
             name="get_token", return_value=creds)
         rv = gcal_helper.validate_and_refresh_creds(initial_credientials)
         assert b'redirect' in rv

    @patch("pulleffect.lib.google.gcal_helper.get_gcal_access_token")
    def test_validate_and_refresh_creds_returns_true(self,mock_get_gcal_access_token ):
        creds = {"hello": "creds"}
        return_val = 'credits'
        mock_get_gcal_access_token.return_value = return_val
        gcal_helper = pulleffect.lib.google.gcal_helper
        rv = gcal_helper.validate_and_refresh_creds(creds)
        rtn = {'access_token': 'credits', 'hello': 'creds'}
        self.assertEqual(rtn,rv)
    @patch('pulleffect.lib.google.gcal_helper.google_get_user')
    def test_get_refresh_token_invalid_username(self,mocked_google_get_user):
        mocked_get_refresh_token_from_username.return_value = None
        rv = gcal_helper.get_refresh_token_from_username("doug")
        self.assertEqual(None,rv)
   
    @patch('pulleffect.lib.google.gcal_helper.google_get_user')
    def test_get_refresh_token_from_username(self,mocked_google_get_user):
        mocked_google_get_user.return_value = {"username":"tharden","google_refresh_token": "120dfkn12390fdsn"}
        rv = gcal_helper.get_refresh_token_from_username("tharden")
        self.assertEqual("120dfkn12390fdsn",rv)

    @patch('pulleffect.lib.google.gcal_helper.google_get_user')
    def test_get_refresh_token_wihtout_username(self,mocked_google_get_user):
        mocked_google_get_user.return_value = ""
        rv = gcal_helper.get_refresh_token_from_username("doug")
        self.assertEqual(None,rv)
    
    @patch('pulleffect.lib.google.gcal_helper.google_get_user')
    def test_get_connected_user_refresh_token(self,mocked_google_get_user):
        mocked_google_get_user.return_value = {"username":"tharden","google_refresh_token": "120dfkn12390fdsn"}
        rv = gcal_helper.get_connected_user_refresh_token("tharden")
        self.assertEqual("120dfkn12390fdsn",rv)

    @patch('pulleffect.lib.google.gcal_helper.google_get_user')
    def test_get_refresh_token_invalid_username(self,mocked_google_get_user):
        mocked_google_get_user.return_value = None
        rv = gcal_helper.get_connected_user_refresh_token("doug")
        self.assertEqual(None,rv)

    @patch('pulleffect.lib.google.gcal_helper.google_get_user')
    def test_get_refresh_token_wihtout_username(self,mocked_google_get_user):
        mocked_google_get_user.return_value = ""
        rv = gcal_helper.get_connected_user_refresh_token("doug")
        self.assertEqual(None,rv)

    """start of gcal test cases"""

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


    """timeclock test cases"""

    @patch("pulleffect.lib.timeclock.timeclock_objects.TimeclockOracleQuery_construct")
    @patch("pulleffect.lib.timeclock.timeclock_helper.try_get_timeclock_entries")
    def test_index_timeclock_clocked_in(self,mocked_try_get_timeclock_entries,mocked_TimeclockOracleQuery_construct):
        params = json.dumps({
                "username" : "Tharden",
                "time_in" : "1200",
                "time_out": "",
                "depts": "(events)",
                "limit": '12',
                "clocked_in": "true"
            })
        mocked_TimeclockOracleQuery_construct.return_value = 'done'
        mocked_try_get_timeclock_entries.return_value = {
        "1200": "1402",'1000':"2300","1230":"1430"
        }
        rv = self.app.get('/timeclock',data = params,content_type = 'application/json')  
        self.assertEqual('1200',rv.data)

    """message test cases"""
    def test_post_single_message(self):
        """POST a single message should succeed"""
        message = json.dumps({
            "device": "wamdamdam",
            "device_type": "brian",
            "location": "hamsterville",
            "severity": "seriously important",
            "description": "this is a description"
        })

        rv = self.app.post('/messages', data=message,
                           follow_redirects=True,
                           content_type='application/json')
        assert b'id' in rv.data

    def test_post_empty_message(self):
        """POST an empty message should result in error"""

        rv = self.app.post('/messages', follow_redirects=True)
        assert b'error' in rv.data

    def test_post_missing_device_message(self):
        """POST a message missing the device field should give error"""
        message = json.dumps({
            "device_type": "brian",
            "location": "hamsterville",
            "severity": "seriously important",
            "description": "this is a description"
        })

        rv = self.app.post(
            '/messages', data=message,
            follow_redirects=True, content_type='application/json')
        assert b'Submitted message is missing required fields' in rv.data

    def test_post_missing_device_type_message(self):
        """POST a message with device type field missing, should give error"""
        message = json.dumps(
            {
                "device": "wamdamdam",
                "location": "hamsterville",
                "severity": "seriously important",
                "description": "this is a description"
            })

        rv = self.app.post('/messages', data=message,
                           follow_redirects=True,
                           content_type='application/json')
        assert b'Submitted message is missing required fields' in rv.data

    def test_post_missing_location_message(self):
        """POST a message missing location field should give error"""
        message = json.dumps(
            {
                "device": "wamdamdam",
                "device_type": "brian",
                "severity": "seriously important",
                "description": "this is a description"
            })

        rv = self.app.post('/messages', data=message,
                           follow_redirects=True,
                           content_type='application/json')
        assert b'Submitted message is missing required fields' in rv.data

    def test_post_missing_severity_message(self):
        """POST a message missing severity field should give error"""
        message = json.dumps({
            "device": "wamdamdam",
            "device_type": "brian",
            "location": "hamsterville",
            "description": "this is a description"
        })

        rv = self.app.post('/messages', data=message,
                           follow_redirects=True,
                           content_type='application/json')
        assert b'Submitted message is missing required fields' in rv.data

    def test_post_missing_description_message(self):
        """POST a message missing description field should give error"""
        message = json.dumps({
            "device": "wamdamdam",
            "device_type": "brian",
            "location": "hamsterville",
            "severity": "seriously important"
        })

        rv = self.app.post('/messages', data=message,
                           follow_redirects=True,
                           content_type='application/json')
        assert b'Submitted message is missing required fields' in rv.data

    """note test cases"""
    
    def test_post_empty_note(self):
        """POST an empty note should fail"""

        rv = self.app.post('/notes', follow_redirects=True)
        assert b'error' in rv.data

    def test_post_note(self):
        note = json.dumps({
            "text": "wamdamdam",
            "author": "brian"
        })

        rv = self.app.post('/notes', data=note,
                           follow_redirects=True,
                           content_type='application/json')
        assert b'id' in rv.data

    def test_post_missing_text_note(self):
        note = json.dumps({
            "author": "brian"
        })

        rv = self.app.post('/notes', data=note,
                           follow_redirects=True,
                           content_type='application/json')

        assert (b"text, Submitted note is missing "
                "required fields: text" in rv.data)

if __name__ == '__main__':
    unittest.main()
#@patch('pulleffect.lib.google.gcal_helper.get_calendar_events')
#def test_calendar_events_gcal(self,mock_get_calendar_events):
#   mock_get_calendar_events.return_value = rtn = {'event': 'description'}
#   rv = self.app.get('/gcal/calendar_events')
#   assert b'description' in rv.data    

#@patch('pulleffect.lib.google.gcal_helper.get_google_auth_uri_from_username')
#def test_authenticate_shifts(self,mock_get_google_auth_uri_from_username):
#    mock_get_google_auth_uri_from_username.return_value = 'correct.uri'
#   rv = self.app.get('/shifts/authenticate')
#    assert b'correct.uri' in rv.data

#@patch('pulleffect.lib.google.gcal_helper.try_validate_google_authorization_code')
#def test_oauth2_callback_shifts(self, mock_try_validate_google_authorization_code):
#    mock_try_validate_google_authorization_code.return_value = 'validation works!'
#    rv = self.app.get('/shifts/oauth2callback')
#    assert b'redirect' in rv.data

#@patch('pulleffect.lib.google.gcal_helper.get_calendar_list')
#def test_calendar_list_shifts(self,mock_get_calendar_list):
#    mock_get_calendar_list.return_value = rtn = {'calendar': 'list of items'}
#    rv = self.app.get('/shifts/calendar_list')
#    assert b'list of items'in rv.data

