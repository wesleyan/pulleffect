# Timeclock entry model
class TimeclockEntry:
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
    def __init__(self, username, time_in, time_out, error_message):
        self.username = username
        self.time_in = time_in
        self.time_out = time_out
        self.error_message = error_message


# Timeclock oracle query
class TimeclockOracleQuery:
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
