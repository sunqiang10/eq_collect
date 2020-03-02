from app import db
from sqlalchemy import Column, String, Integer, DateTime, Float
import datetime


class Reporter(db.Model):
    __tablename__ = "t_report"
    id = Column(Integer, primary_key=True, autoincrement=True)
    Cata_id = db.Column(String(255))
    currenLat = db.Column(Float(10))
    currenLon = db.Column(Float(10))
    fell = db.Column(String(255))
    house = db.Column(String(255))
    person = db.Column(String(255))
    content = db.Column(String(255))
    open_id = db.Column(String(255))
    c_addr = db.Column(String(255))

    is_share = db.Column(Integer, default=0)
    is_wx = db.Column(Integer, default=1)
    updatetime = db.Column(DateTime, default=datetime.datetime.now)
