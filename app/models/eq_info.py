from app import db
from sqlalchemy import Column, String, Integer, DateTime, Float
import datetime


class EqInfo(db.Model):
    __tablename__ = "cata7days"
    # id = Column(Integer , primary_key=True , autoincrement=True)
    Cata_id = db.Column(String(40), primary_key=True)
    Eq_type = db.Column(Integer)
    O_time = db.Column(DateTime, default=datetime.datetime.utcnow)
    Lat = db.Column(Float(10))
    Lon = db.Column(Float(10))
    geom = db.Column(String(100))
    Depth = db.Column(Float(10))
    M = db.Column(Float(10))
    Location_cname = db.Column(String(128))
    is_create_pic = db. Column(Integer)

    def __init__(self, **items):
        for key in items:
            if hasattr(self, key):
                setattr(self, key, items[key])

    def __str__(self):
        return "<EqInfo(Cata_id %s,Location_cname %s)>" % (self.Cata_id, self.Location_cname)
