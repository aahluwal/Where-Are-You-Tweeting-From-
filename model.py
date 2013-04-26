from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, create_engine, Float
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime 
import os
import json
from app import db
session = db.session
#db_uri = os.environ.get("DATABASE_URL", "postgresql://localhost/twitter")
#db_uri = os.environ.get("DATA_BASE_URL", "sqlite:///twitter.db")
#engine = create_engine(db_uri, echo=False)
#session = scoped_session(sessionmaker(bind=engine,
#				      autocommit = False,
#				      autoflush = False))

#Base = declarative_base()
#Base.query = session.query_property

class Container(db.Model):
    __tablename__ = "containers"
    id = Column(Integer, primary_key = True)
    key = Column(String(128), nullable = False)
    value = Column(String(2000000), nullable=False)


class Tweet(db.Model):
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

class Features(db.Model):
    __tablename__ = 'features'
    
    id = Column(Integer, primary_key=True)
    city_features = Column(String(1000000), nullable=False)
    city_name = Column(String(128), nullable=False) 

    def list_of_features(self):
	features = json.loads(self.city_features)
	return features 

class Los_Angeles():
    def __init__(self):
	#los_angeles = Los_Angeles()
	self.lon = -118.2436
	self.lat = 34.0522
	self.name = 'Los Angeles'

class San_Francisco():
    def __init__(self):
	#san_francisco = San_Francisco()
	self.lon = -122.416534
	self.lat = 37.781569
	self.name = 'San Francisco'

class Houston():
    def __init__(self):
	self.lon = -95.369
	self.lat = 29.760
	self.name = 'Houston'
	#houston = Houston()

class Atlanta():
    def __init__(self):
	self.lon = -84.3879
	self.lat = 33.749
	self.name = 'Atlanta'
	#atlanta = Atlanta()

class New_York():
    def __init__(self):
	self.lon = -73.951721
	self.lat = 40.703546
	self.name = 'New York'
	#new_york = New York()

class Chicago():
    def __init__(self):
	self.lon = -87.6298
	self.lat = 41.878
	self.name= 'Chicago'
	#chicago = Chicago()

class Miami(): 
    def __init__(self):
	self.lon = -80.2264
	self.lat = 25.7889
	self.name = 'Miami'
	#miami = Miami()

class Seattle():
    def __init__(self):
	self.lon= -122.33
	self.lat=47.609
	self.name='Seattle'

class Boston():
    def __init__(self):
	self.lon = -71.0603
	self.lat = 42.3583
	self.name = 'Boston'

    
def create_db():
    Base.metadata.create_all(engine)

def main():
    """In case we need this for something"""
    pass

if __name__ == "__main__":
    main()
