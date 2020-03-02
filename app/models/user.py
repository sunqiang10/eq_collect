from app import db
from sqlalchemy import Column, String, Integer, DateTime, Float
import datetime


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), index=True, unique=True)
    password = db.Column(db.String(255), index=False, unique=False)
    state = db.Column(db.String(255), index=False, unique=False)
    p_user = db.Column(db.String(255), index=False, unique=False)
    email = db.Column(db.String(255), index=False, unique=False)
    nickname = db.Column(db.String(255), index=False, unique=False)
    sex = db.Column(db.String(255), index=False, unique=False)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)  # python 3

    def __repr__(self):
        return '<User %r>' % self.username


class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post %r>' % self.body
