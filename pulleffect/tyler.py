import os
#import flaskr
import unittest
import tempfile

class tylerPrintSeq():

	def run():
		 """Before each test, set up a blank database"""
        self.db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
        flaskr.app.config['TESTING'] = True
        self.app = flaskr.app.test_client()
        flaskr.init_db()

        for i in range(0,10):
   			print(self.app.get('/notes?limit={0}'.format(i)))