import os
DEBUG = True
S_PORT = 9790
SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root:123456@127.0.0.1:3306/eq'
basedir = os.path.abspath(os.path.dirname(__file__))
CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess-'
OPENID_PROVIDERS = [
    { 'name': 'SunQiang', 'url': 'http://sunqiang.openid.org.cn/'},
    { 'name': 'Google', 'url': 'https://www.google.com/accounts/o8/id'},
    { 'name': 'Yahoo', 'url': 'https://me.yahoo.com'},
    { 'name': 'AOL', 'url': 'http://openid.aol.com/<username>'},
    { 'name': 'Flickr', 'url': 'http://www.flickr.com/<username>'},
    { 'name': 'MyOpenID', 'url': 'https://www.myopenid.com'}]
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_COMMIT_TEARDOWN = True
SQLALCHEMY_POOL_RECYCLE = 120
