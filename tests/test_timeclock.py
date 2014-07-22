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

    @patch("pulleffect.lib.timeclock.timeclock_objects.TimeclockOracleQuery_construct")
    @patch("pulleffect.lib.timeclock.timeclock_helper.try_get_timeclock_entries")
    def test_index_timeclock_clocked_in(self,mocked_try_get_timeclock_entries,mocked_TimeclockOracleQuery_construct):
        params = json.dumps({
                "username" : "Tharden",
                "time_in" : "1200",
                "time_out": "1220",
                "depts": "(events)",
                "limit": '12',
                "clocked_in": "true"
            })
        mocked_TimeclockOracleQuery_construct.return_value = 'done'
        mocked_try_get_timeclock_entries.return_value = {"1200": "1402"}
        rv = self.app.get('/timeclock?username=Tharden&time_in=1200&time_out=1330&depts=(events)&limit=12&clocked_in=True')
        self.assertEqual('{\n  "1200": "1402"\n}',rv.data)

    @patch("pulleffect.lib.timeclock.timeclock_objects.TimeclockOracleQuery_construct")
    @patch("pulleffect.lib.timeclock.timeclock_helper.try_get_timeclock_entries")
    def test_index_timeclock_clocked_out(self,mocked_try_get_timeclock_entries,mocked_TimeclockOracleQuery_construct):
        params = {
                "username" : "Tharden",
                "time_in" : "1200",
                "time_out": "1220",
                "depts": "(events)",
                "limit": '12',
                "clocked_in": "False"
            }
        mocked_TimeclockOracleQuery_construct.return_value = 'done'
        mocked_try_get_timeclock_entries.return_value = {"1200": "1402"}
        rv = self.app.get('/timeclock?username=Tharden&time_in=1200&time_out=1330&depts=(events)&limit=12&clocked_in=False')
        self.assertEqual('{\n  "1200": "1402"\n}',rv.data)

    def test_index_timeclock_wrong_dept(self):
        rv = self.app.get('/timeclock?username=tharden&time_in=1200&time_out=1300&depts=(partyparty)&limit=10&clocked_in=True')
        assert b'Invalid parameter' in rv.data

    def test_index_timeclock_wrong_limit(self):
        rv = self.app.get('/timeclock?username=tharden&time_in=1200&time_out=1300&depts=(events)&limit=dog&clocked_in=True')
        assert b'Invalid parameter' in rv.data
    def test_index_timeclock_wrong_time_out(self):
        rv = self.app.get('/timeclock?username=tharden&time_in=1200&time_out=dog&depts=(events)&limit=10&clocked_in=False')
        assert b'Invalid parameter' in rv.data
    def test_index_timeclock_wrong_time_in(self):
        rv = self.app.get('/timeclock?username=tharden&time_in=dog&time_out=1000&depts=(events)&limit=10&clocked_in=False')
        assert b'Invalid parameter' in rv.data
    @patch("pulleffect.lib.timeclock.timeclock_helper.check_for_unicode_username")
    def test_index_timeclock_wrong_username(self,mocked_check_for_unicode_username):
        mocked_check_for_unicode_username.return_value = "No unicode allowed: 'username'"
        rv = self.app.get('/timeclock?username=thardentime_in=1200&time_out=1000&depts=(events)&limit=10&clocked_in=False')
        assert b'No unicode allowed' in rv.data
    @patch("pulleffect.lib.timeclock.timeclock_helper.is_departments_unicode")
    def test_index_timeclock_wrong_username(self,mocked_is_departments_unicode):
        mocked_is_departments_unicode.return_value = "No unicode allowed: 'username'"
        rv = self.app.get('/timeclock?username=?????????&time_in=dog&time_out=1000&depts=(events)&limit=10&clocked_in=False')
        assert b'No unicode allowed' in rv.data

if __name__ == '__main__':
    unittest.main()
