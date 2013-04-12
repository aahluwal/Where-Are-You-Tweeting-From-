from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, create_engine, Float
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime 

engine = create_engine("postgresql://localhost/twitter", echo=False)
session = scoped_session(sessionmaker(bind=engine,
				      autocommit = False,
  				      autoflush = False))

Base = declarative_base()
Base.query = session.query_property


class Tweet(Base):
    __tablename__ = "tweets"

    id = Column(Integer, primary_key = True)
    screename = Column(String(500), nullable = False)
    text = Column(String(500), nullable = False)
    longitude = Column(Float(precision=6), nullable = False)
    latitude = Column(Float(precision=6), nullable = False) 
    created_at = Column(DateTime , nullable = True)

    def __repr__(self):
        return 'Tweet: %d %s %s %s %f %f' % (
		self.id,
		self.screename.encode('utf-8'),
		self.text.encode('utf-8'),
		self.created_at,
		self.longitude,
		self.latitude
		)

    def __str__(self):
	return self.__repr__()

    @classmethod  
    def create_from_dict(cls, dict):
        tweet = Tweet()
	tweet.screename = dict.get('screen_name')
	tweet.text = dict.get('text')
	tweet.created_at = datetime.strptime(dict.get('created_at'), '%Y-%m-%dT%H:%M:%S')
	#tweet.created_at = datetime.strptime(dict.get('created_at'), 'datetime.datetime(%Y, %m, %d, %H, %M, %S)')
	geo_location = dict.get('coordinates')
	coordinate_list = geo_location.get('coordinates')
	tweet.longitude = coordinate_list[0]
	tweet.latitude = coordinate_list[1]
	return tweet



class Los_Angeles():
    def __init__(self):
	#los_angeles = Los_Angeles()
	self.lon = -118.2436
	self.lat = 34.0522

class San_Francisco():
    def __init__(self):
	#san_francisco = San_Francisco()
	self.lon = -122.75
	self.lat = 36.8

class Houston():
    def __init__(self):
	self.lon = -95.369
	self.lat = 29.760
	#houston = Houston()

class Atlanta():
    def __init__(self):
	self.lon = -84.3879
	self.lat = 33.749
	#atlanta = Atlanta()

class New_York():
    def __init__(self):
	self.lon = -74
	self.lat = -40
	#new_york = New_York()

class Chicago():
    def __init__(self):
	self.lon = -87.6298
	self.lat = 41.878
	#chicago = Chicago()

class Miami(): 
    def __init__(self):
	self.lon = -80.2264
	self.lat = 25.7889
	#miami = Miami()
    
def create_db():
    Base.metadata.create_all(engine)

def main():
    """In case we need this for something"""
    pass

if __name__ == "__main__":
    main()
