from flask import Flask
import config
from flask_sqlalchemy import SQLAlchemy
import pymysql
from flask_login import LoginManager
from apscheduler.schedulers.background import BackgroundScheduler
from flask_cors import CORS

# 用py_mysql替换MySQLdb
pymysql.install_as_MySQLdb()
app = Flask(__name__, template_folder='../templates', static_folder="../static")
app.config.from_object(config)
db = SQLAlchemy(app)

from app.user_view import user_blue
from app.report_view import report_blue
from app.wx import wx_blue

app.register_blueprint(user_blue)
app.register_blueprint(report_blue)
app.register_blueprint(wx_blue)

# CORS(app, supports_credentials=True)
# 数据库

# 登录表单
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
lm.login_message = u'请先登录'
# 定时任务-用来更新图片
scheduler = BackgroundScheduler()
scheduler.start()
