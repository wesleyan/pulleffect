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


class TimeclockOracleQuery:
    """Represents an Oracle SQL query constructed for timeclock entries.

        Attributes:
            username -- query finds timeclock entries belonging to username
            time_in -- query finds timeclock entries occurring after time_in
            time_out -- query finds timeclock entries occurring before time_out
            job_ids -- query finds timeclock_entries with given job_ids
            limit -- query finds a maximum of 'limit' timeclock entries
    """
    # TODO(arthurb): This method can probably be refactored
    def __init__(self, username, time_in, time_out,
                 job_ids, limit, clocked_in):
        # The stuff that probably won't ever change
        select_clause = ("SELECT * FROM (SELECT USERNAME, TIME_IN, TIME_OUT, "
                         "JOB_ID, NOTE FROM ACLC_USDAN.NED_SHIFT ORDER BY "
                         "TIME_IN DESC) ")

        # Converts datetime objects to timestamps in SQL
        sql_timestamp = ("(TO_DATE('19700101','yyyymmdd') +"
                         " (TO_NUMBER({0})/24/60/60))")

        self.named_params = {}

        # Build time_in, time_out, and where clauses
        if clocked_in:
            where_clause = "WHERE TIME_OUT IS NULL AND JOB_ID IN "
        else:
            time_in_clause = sql_timestamp.format(':time_in')
            time_out_clause = sql_timestamp.format(':time_out')
            where_clause = (
                "WHERE TIME_IN >={0} AND TIME_OUT <={1} AND JOB_ID IN "
                .format(time_in_clause, time_out_clause)
            )
            self.named_params['time_in'] = time_in
            self.named_params['time_out'] = time_out

        # Build SQL array with job ids
        job_id_clause = "("
        for i in range(len(job_ids)):
            job_id = 'job_id{0}'.format(str(i))
            self.named_params[job_id] = job_ids[i]
            job_id_clause += ":{0},".format(job_id)

        # Append job ids to WHERE clause
        where_clause += job_id_clause[:-1] + ")"

        # Append username to WHERE clause, if given
        if username:
            where_clause += " AND USERNAME=:username"
            self.named_params['username'] = username

        # Append the limit
        if not clocked_in:
            where_clause += " AND ROWNUM <=:limit"
            self.named_params['limit'] = limit

        # Completed query
        self.query = "{0}{1}".format(select_clause, where_clause)
