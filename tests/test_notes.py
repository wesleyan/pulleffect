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

timeclock_helper = pulleffect.lib.timeclock.timeclock_helper
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