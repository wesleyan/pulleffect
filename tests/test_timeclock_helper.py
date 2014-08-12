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
    @patch("pulleffect.lib.timeclock.timeclock_objects.TimeclockEntry")
    def test_build_timeclock_entries(self,mocked_TimeclockEntry):
        mocked_TimeclockEntry.return_value = ["timeclock_entries"]
        rv = pulleffect.lib.timeclock.timeclock_helper.build_timeclock_entries({'timeclock_entries': 'description'})
        self.assertEqual([['timeclock_entries']],rv)

    @patch("pulleffect.lib.timeclock.timeclock_objects.TimeclockEntry")
    def test_build_timeclock_without_entries(self,mocked_TimeclockEntry):
        mocked_TimeclockEntry.return_value = []
        rv = pulleffect.lib.timeclock.timeclock_helper.build_timeclock_entries({'timeclock_entries': 'description'})
        self.assertEqual([[]],rv)

    def test_check_for_unicode_username_ascii(self):
        rv = pulleffect.lib.timeclock.timeclock_helper.check_for_unicode_username("dog")
        self.assertEqual(None,rv)
    def test_check_unicode_username_with_unicode(self):
        username = unicode('dog')
        rv = pulleffect.lib.timeclock.timeclock_helper.check_for_unicode_username(username)
        self.assertEqual(None,rv)
    def test_is_departments_unicode(self):
        rv = pulleffect.lib.timeclock.timeclock_helper.is_departments_unicode("events")
        self.assertEqual(False,rv)
    def test_is_departments_unicode(self):
        departments = unicode("events")
        rv = pulleffect.lib.timeclock.timeclock_helper.is_departments_unicode(departments)
        self.assertEqual(False,rv)

if __name__ == '__main__':
    unittest.main()
