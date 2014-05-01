from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import Column
# from sqlalchemy import DateTime
# from sqlalchemy import String
from sqlalchemy import MetaData
from sqlalchemy import Table
from pulleffect.lib.utilities import wes_timeclock_engine

Base = declarative_base()
metadata = MetaData(bind=wes_timeclock_engine)


# Table containing timeclock entries
class TimeclockEntries(Base):
    __table__ = Table('NED_SHIFT', metadata, autoload=True)


# # Timeclock entry from wes timeclock db
# class TimeclockEntry(Base):
#     __tablename__ = 'NED_SHIFT'

#     # Unique username of time clock entry owner
#     username = Column(String(80), unique=True)

#     # Time user clocked in
#     time_in = Column(DateTime())

#     # Time user clocked out
#     time_out = Column(DateTime())

#     def __repr__(self):
#         # Build a print string
#         pstr = "<TimeclockEntry(username='%s', time_in='%s', time_out='%s')>"
#         return pstr % (self.username, self.time_in, self.time_out)
