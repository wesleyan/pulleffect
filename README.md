pulleffect
==========

An application that polls and displays glanceable information from a variety of sources, built on Flask and Backbone.js.


## How do I use it?
1. now you can run the runserver.py file with your
     python interpreter and the application will
     greet you on http://localhost:3000/

## Is it tested?

  Not yet... I sort of broke everything. Some day you'll be able to run the 'pulleffect_tests.py' file to see the tests pass.

## How to start developing? (from root directory of app)

1. sudo easy_install pip
2. sudo pip install virtualenv
3. virtualenv penv
4. ln -s penv/bin/activate
5. source activate
6. pip install -r requirements.txt
7. install and launch mongodb
8. Edit your env.py file by setting beta = False
9. echo env.py > .git/info/exclude
10. git update-index --assume-unchanged pulleffect/config/env.py
11. python runserver.py
12. Direct your web browser to http://localhost:5000

## EXTRA:
  If you want to code for the timeclock widget, you will need Oracle Instantclient 11.2 (basic, sql*plus, and sdk)
  
1. Easiest instructions can be found here: https://help.ubuntu.com/community/Oracle%20Instant%20Client
    1. alien -i oracle-instantclient-basic*.rpm
    2. alien -i oracle-instantclient-sqlplus*.rpm
    3. alien -i oracle-instantclient-devel*.rpm
    4. Add these lines to ~./.bashrc (confirm the files exist before adding them to .bashrc):
        - export ORACLE_HOME="/usr/lib/oracle/11.2/client64"
        - export LD_LIBRARY_PATH="$ORACLE_HOME/lib"
        - export PATH="$ORACLE_HOME:$ORACLE_HOME/bin:$PATH" 
    5. Add this line to a file called /etc/ld.so.conf.d/oracle.conf (make the file if it doesn't exist):
        - /usr/lib/oracle/11.2/client64/lib
    6. Install libaio1 using sudo apt-get install libaio1
    6. Run sudo ldconfig


