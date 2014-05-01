from pulleffect.lib.sqlalchemy import db
from pulleffect.lib.utilities import db_names

# Timeclock entry from wes timeclock db
class TimeclockEntry(db.Model):
	
	# Binds timeclock entry to wes timeclock db
    __bind_key__ = db_names.get('wes_timeclock')

    # Unique username of time clock entry owner
    username = db.Column(db.String(80), unique=True)

    # Time user clocked in
    time_in = db.Column(db.DateTime())

    # Time user clocked out
    time_out = db.Column(db.DateTime())