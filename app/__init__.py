import os
from flask import Flask
import config
from flask_sqlalchemy import SQLAlchemy
import pymysql
from flask_login import LoginManager
from apscheduler.schedulers.background import BackgroundScheduler

# 用py_mysql替换MySQLdb
pymysql.install_as_MySQLdb()
app = Flask(__name__, template_folder='../templates', static_folder="../static")
app.config.from_object(config)
# 数据库
db = SQLAlchemy(app)
# 登录表单
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
lm.login_message = u'请先登录'
# 定时任务-用来更新图片
scheduler = BackgroundScheduler()
scheduler.start()
