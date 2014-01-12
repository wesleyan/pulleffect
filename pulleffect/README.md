                         / Pull Effect /

                 An information consolidation machine or something


    ~ How do I use it?

      1. now you can run the runserver.py file with your
         python interpreter and the application will
         greet you on http://localhost:5000/
	
    ~ Is it tested?

      Not yet... I sort of broke everything. Some day you'll be able to run the 'pulleffect_tests.py' file to see the tests pass.

    ~ How to start developing? (from root directory of app)

      1. sudo easy_install pip
      2. sudo pip install virtualenv
      3. virtualenv penv
      4. ln -s penv/bin/activate
      5. source activate
      6. pip install -r requirements.txt
      7. install and launch mongodb
      7. python runserver.py
      8. Direct your web browser to http://localhost:5000
      9. Signin credentials can be found in config file of __init__.py

    ~ TODO
      1. Add google user registration
      2. Generic widget support



