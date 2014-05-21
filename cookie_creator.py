# Copyright (C) 2014 Wesleyan University
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""The file that creates a full screen room info widget set up,
   with the info of the room number given. It creates an SQL query to update
   the SQLite cookie database of Chromium.

   REQUIRES SQLITE3
   Can be run in command line like this: python cookie_creator.py [room number]

   Example:
   python cookie_creator.py 2
"""
import os
import sys


def cookie_sql(room_number):
    new_value = "%255B%257B%2522type%2522%253A%2522roomInfo%2522%252C%2522selectedRoom%2522%253A" + str(room_number) + "%252C%2522time%2522%253A1394544770196%252C%2522expanded%2522%253Atrue%252C%2522col%2522%253A1%252C%2522row%2522%253A1%252C%2522size_x%2522%253A4%252C%2522size_y%2522%253A4%257D%255D"
    return "REPLACE INTO cookies VALUES(13039018381314651, 'localhost', 'widgets', '" + new_value + "', '/', 13816618381000000, 0, 0, 13039019459531228, 1, 1, 1);"

# Run SQL command on the sqlite database: ~/.config/chromium/Default/Cookies


def run_command(path, room_number):
    os.system("sqlite3 " + path + " \"" + cookie_sql(room_number) + "\"")
    print 'Room ' + str(room_number) + ' updated'

# Default value for no reason
room_to_change = 77
if len(sys.argv[1:]) > 0:
    room_to_change = sys.argv[1:][0]

run_command('~/.config/chromium/Default/Cookies', room_to_change)
