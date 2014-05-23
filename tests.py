import os
import pulleffect
import unittest
import tempfile
import json
 
 
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
 
    def signin(self, username, password):
        return self.app.get('/gplus/signin?', follow_redirects=True)
 
    def signout(self):
        return self.app.get('/gplus/signout', follow_redirects=True)
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