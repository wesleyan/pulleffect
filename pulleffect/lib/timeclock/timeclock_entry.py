from pulleffect.lib.databases import db


class TimeclockEntry(db.Model):
    __tablename__ = 'NED_SHIFT'

    # Id
    id = db.Column('ID', db.Integer, primary_key=True)

    # Username
    username = db.Column('USERNAME', db.String(80))

    # Time in
    time_in = db.Column('TIME_IN', db.DateTime())

    #Time out
    time_out = db.Column('TIME_OUT', db.DateTime())
