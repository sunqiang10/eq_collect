from app import db


class WxConfig(db.Model):
    __tablename__ = "wx_config"
    id = db.Column(db.Integer, primary_key=True)
    appid = db.Column(db.String(255), index=True, unique=True)
    secret = db.Column(db.String(255), index=False, unique=False)

