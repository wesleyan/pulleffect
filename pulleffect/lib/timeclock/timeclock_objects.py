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


# Timeclock entry model
class TimeclockEntry:
    """Represents a timeclock entry from Oracle database.

        Attributes:
            username -- username of person who clocked in
            time_in -- time the person who clocked in
            time_out -- time the person who clocked out (can be None)
            dept -- department for which the person clocked in
            note -- note the person left for the given timeclock entry
    """
    def __init__(self, username, time_in, time_out, dept, note):
        self.username = username
        self.time_in = time_in
        self.time_out = time_out
        self.dept = dept
        self.note = note

    # Serializes the object into a dictionary so it can be jsonified
    def serialize(self):
        return {
            'username': self.username,
            'time_in': self.time_in,
            'time_out': self.time_out,
            'dept': self.dept,
            'note': self.note
        }


# Timeclock request object
class TimeclockRequest:
    """Represents the timeclock request for the database to process.

        Attributes:
            username -- username of person who clocked in
            time_in -- time the person who clocked in
            time_out -- time the person who clocked out (can be None)
            job_ids -- job ids that represent departments
            error_message -- explains why the timeclock request is invalid
    """
    def __init__(self, username, time_in, time_out, job_ids, error_message):
        self.username = username
        self.time_in = time_in
        self.time_out = time_out
        self.job_ids = job_ids
        self.error_message = error_message


# Timeclock oracle query
class TimeclockOracleQuery:
    """Represents an Oracle SQL query constructed for timeclock entries.

        Attributes:
            username -- query finds timeclock entries belonging to username
            time_in -- query finds timeclock entries occurring after time_in
            time_out -- query finds timeclock entries occurring before time_out
            job_ids -- query finds timeclock_entries with given job_ids
    """
    def __init__(self, username, time_in, time_out, job_ids):
        # The stuff that probably won't ever change
        select_clause = ("SELECT * FROM (SELECT USERNAME, TIME_IN, TIME_OUT, "
                         "JOB_ID, NOTE FROM ACLC_USDAN.NED_SHIFT ORDER BY "
                         "TIME_IN DESC) ")

        # Converts datetime objects to timestamps in SQL
        sql_timestamp = ("(TO_DATE('19700101','yyyymmdd') +"
                         " (TO_NUMBER({0})/24/60/60))")

        # Build time in and time out clauses
        time_in_clause = sql_timestamp.format(':time_in')
        time_out_clause = sql_timestamp.format(':time_out')

        # Edit later if you ever need to tweak the WHERE clause
        where_clause = "WHERE TIME_IN >={0} AND TIME_OUT <={1} AND JOB_ID IN "
        where_clause = where_clause.format(time_in_clause, time_out_clause)

        # Named params that fill in the 'where_clause'
        named_params = {'time_in': time_in, 'time_out': time_out}

        # Build SQL array with job ids
        job_id_clause = "("
        for i in range(len(job_ids)):
            job_id = 'job_id{0}'.format(str(i))
            named_params[job_id] = job_ids[i]
            job_id_clause += ":{0},".format(job_id)

        # Add job ids to WHERE clause
        where_clause += job_id_clause[:-1] + ")"

        # Append the username if it was given
        if username is not None:
            where_clause += " AND USERNAME=:username"
            named_params['username'] = username

        # Completed query
        query = "{0}{1}".format(select_clause, where_clause)

        self.query = query
        self.named_params = named_params
