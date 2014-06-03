import os
import pulleffect
import unittest
import tempfile
import json
import inspect
from pulleffect.lib.google.gcal_helper import get_google_auth_uri_from_username
from mock import patch 
from mock import MagicMock

class TestCCase(unittest.TestCase):
 
    def setUp(self):
        """Before each test, set up a blank database
 
        """
        self.db_fd, pulleffect.app.config['DATABASE'] = tempfile.mkstemp()
        pulleffect.app.config['TESTING'] = True
        self.app = pulleffect.app.test_client()
 
    def tearDown(self):
        """Get rid of the database again after each test."""
        os.close(self.db_fd)
        os.unlink(pulleffect.app.config['DATABASE'])

    def test_get_calendar_list_for_gcalhelper_without_credentials(self):      
        rtn = { "redirect": "/gcal/authenticate"}       
        pulleffect.lib.google.gcal_helper.validate_and_refresh_creds = MagicMock(name = "sup", return_value  = rtn)
        pulleffect.lib.google.gcal_helper.get_google_creds = MagicMock(name = "sup2", return_value  = "redirect")
        credentials = pulleffect.lib.google.gcal_helper.get_calendar_list("name","widget")
        assert b'redirect' in credentials

    def test_get_calendar_list_for_gcalhelper(self):
        rtn = { "correct": "credentials"}       
        rtn_cal = ('items', 'summary', 'events', 'id' 'items', 'summary', 'events', 'id');
        pulleffect.lib.google.gcal_helper.validate_and_refresh_creds = MagicMock(name = "validate_creds", return_value  = rtn)
        pulleffect.lib.google.gcal_helper.get_google_creds = MagicMock(name = "get_creds", return_value  = "creds")
        pulleffect.lib.google.gcal_helper.get_gcal_service_from_credentials = MagicMock(name = rtn_cal)
        pulleffect.lib.google.gcal_helper.set_google_creds = MagicMock(name = 'set_creds', return_value = 'done')
        calendar_list = pulleffect.lib.google.gcal_helper.get_calendar_list("name","widget")
        print(calendar_list)
        assert b'items' in calendar_list

    def test_get_calendar_events_no_creds(self):
        rtn = { "redirect": "/gcal/authenticate"}        
        pulleffect.lib.google.gcal_helper.validate_and_refresh_creds = MagicMock(name = "validate_creds", return_value  = rtn)
        pulleffect.lib.google.gcal_helper.get_google_creds = MagicMock(name = "get_creds", return_value  = "creds")
        events = pulleffect.lib.google.gcal_helper.get_calendar_events(123512,1200,1500,"name","widget")
        assert b'redirect' in events
   
    #def test_get_calendar_events(self):
     #   rtn = { "correct": "credentials"}

      #  pulleffect.lib.google.gcal_helper.validate_and_refresh_creds = MagicMock(name = "validate_creds", return_value  = rtn)
       # pulleffect.lib.google.gcal_helper.get_google_creds = MagicMock(name = "get_creds", return_value  = "creds")
        #pulleffect.lib.google.gcal_helper.get_gcal_service_from_credentials = MagicMock(name = "get_service")
        #pulleffect.lib.google.gcal_helper.set_google_creds = MagicMock(name = 'set_creds', return_value = 'done')
        #events = pulleffect.lib.google.gcal_helper.get_calendar_events(123512,1200,1500,"name","widget")
        #assert b'' in events





    @patch('pulleffect.lib.google.gcal_helper.get_google_auth_uri_from_username')
    def test_authenticate_gcal(self,mock_get_google_auth_uri_from_username):
        mock_get_google_auth_uri_from_username.return_value = 'correct.uri'
        rv = self.app.get('/gcal/authenticate')     
        assert b'correct.uri' in rv.data
    
    @patch('pulleffect.lib.google.gcal_helper.try_validate_google_authorization_code')
    def test_oauth2_callback_gcal(self, mock_try_validate_google_authorization_code):
    	mock_try_validate_google_authorization_code.return_value = 'validation works!'
    	rv = self.app.get('/gcal/oauth2callback')
    	assert b'redirect' in rv.data

    @patch('pulleffect.lib.google.gcal_helper.get_calendar_list')
    def test_calendar_list_gcal(self,mock_get_calendar_list):
    	mock_get_calendar_list.return_value = rtn = {'calendar': 'list of items'}
    	rv = self.app.get('/gcal/calendar_list')
    	assert b'list of items'in rv.data

    def test_post_single_message(self):
        """POST a single message should succeed"""
        message = json.dumps(
        {
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
        message = json.dumps(
            {
                
                "device_type": "brian",
                "location": "hamsterville",
                "severity": "seriously important",
                "description": "this is a description"
            })
 
        rv = self.app.post('/messages', data=message,
                           follow_redirects=True,
                           content_type='application/json')
        assert b'Submitted message is missing required fields' in rv.data

    def test_post_missing_device_type_message(self):
        """POST a message with the device type field missing should give error"""
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
        message = json.dumps(
        {
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
        message = json.dumps(
            {
                "device": "wamdamdam",
                "device_type": "brian",
                "location": "hamsterville",
                "severity": "seriously important"
           })
 
        rv = self.app.post('/messages', data=message,
                           follow_redirects=True,
                           content_type='application/json')
        assert b'Submitted message is missing required fields' in rv.data

    def test_post_empty_note(self):
        """POST an empty note should fail"""
 
        rv = self.app.post('/notes', follow_redirects=True)
        assert b'error' in rv.data
    def test_post_note(self):
        note = json.dumps(
            {
                "text": "wamdamdam",
                "author": "brian"
           })
 
        rv = self.app.post('/notes', data=note,
                           follow_redirects=True,
                           content_type='application/json')
        assert b'id' in rv.data
    def test_post_missing_text_note(self):
        note = json.dumps(
            {
                "author": "brian"
           })
 
        rv = self.app.post('/notes', data=note,
                           follow_redirects=True,
                           content_type='application/json')

        assert b"text, Submitted note is missing required fields: text"in rv.data
    def test_post_note(self):
        note = json.dumps(
            {
                "text": "wamdamdam",
           })
 
        rv = self.app.post('/notes', data=note,
                           follow_redirects=True,
                           content_type='application/json')
        assert b'author, Submitted note is missing required fields: author' in rv.data




        
if __name__ == '__main__':
    unittest.main()



''''commented out the shifts tests, as vagrant does not currently install cx_oracle'''

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




