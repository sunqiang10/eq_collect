from flask import render_template, flash, redirect, session, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from app.models.eq_info import EqInfo
from app.models.user import User
from app import app, db, lm, scheduler
from .forms import LoginForm
from app.utils import serialize
import hashlib
import logging
import threading
import urllib.request
import os
import urllib
from flask_cors import cross_origin
mylock = threading.Lock()


# flask后端
@app.route('/')
@app.route('/index')
@login_required
def index():
    user = g.user
    return render_template('index.html', title='Home', user=user,
                           eqInfos=EqInfo.query.order_by(EqInfo.O_time.desc()).limit(100).all())


@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@cross_origin(supports_credentials=True)
@app.before_request
def before_request():
    print(session)
    url_accept = ["/login_view", "/login", "/user/user_login", "/wx/wechat", "/wx/login4wx", "/wx/wx_login"]
    g.user = current_user
    ss = request.path.split('/')
    if len(ss) > 1 and ss[1] == 'static':
        pass
    else:
        if request.path in url_accept:
            pass
        else:
            if 'username' in session:
                pass
            else:
                return redirect(url_for('login_view'))


@app.route('/login_view', methods=['GET', 'POST'])
def login_view():
    form = LoginForm()
    return render_template('login.html', title="Sign In", form=form)


# 后端flask用户登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user_name = request.form.get('username', None)
        password = request.form.get('password', None)
        pw = hashlib.md5(password.encode(encoding='UTF-8')).hexdigest()
        print(pw)
        remember_me = request.form.get('remember_me', False)
        user = User.query.filter_by(username=user_name).first()
        if not user:
            flash('用户不存在.')
            return redirect(url_for('login_view'))
        if pw != user.password:
            flash('用户密码不正确.')
            return redirect(url_for('login_view'))
        else:
            login_user(user, remember=remember_me)
            session['username'] = user.username
            return redirect(request.args.get('next') or url_for('index'))
    return render_template('login.html', title="Sign In", form=form)


@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('index'))


# 定期清理无用图片
def clean_img():
    path = serialize.STATIC_FILE_PATH + 'upload' + os.sep
    dirs = os.listdir(path)
    for file in dirs:
        data = db.session.execute('SELECT COUNT(1) from t_report where instr(pic_path,\''
                                  + file + '\') > 0')
        row = data.fetchone()  # 取第一条
        if row[0] == 0:
            os.remove(path+file)
    db.close_all_sessions()


clean_img()


# flask后端生成震中百度地图图片
def create_pic():
    mylock.acquire()
    try:
        root_path = os.path.abspath(os.path.dirname(__file__)).split('eq_collect')[0]
        datas = EqInfo.query.order_by(EqInfo.O_time.desc()).limit(100).all()
        for data in datas:
            if data.is_create_pic == 0:
                file_path = root_path + 'eq_collect' + os.sep + 'static' + os.sep \
                            + 'img' + os.sep + data.cata_id + '.png'
                img_url = "http://api.map.baidu.com/staticimage?width=240&height=320&center=" \
                          + str(data.Lon) + "," + str(data.Lat) + "&zoom=8&markers=" \
                          + str(data.Lon) + "," + str(data.Lat) \
                          + "&markerStyles=-1,-1,25,25&copyright=1"
                print('file_path:', file_path)
                result = download_img(img_url, file_path)
                print(result)
                if result:
                    data.is_create_pic = 1
                    db.session.commit()

    except Exception as e:
        logging.error(e)
    finally:
        mylock.release()
        db.close_all_sessions()


def download_img(img_url, file_path):
    print('img_url:', img_url)
    if not os.path.exists(file_path):
        return urllib.request.urlretrieve(img_url, file_path)


# 定时任务，生成图片
def run_task():
    scheduler.add_job(create_pic, 'cron', minute='55')
    # scheduler.add_job(create_pic, 'interval', seconds=60)
    # scheduler.add_job(func=aps_test, args=('定时任务',), trigger='cron', second='*/5')
    # scheduler.add_job(func=aps_test, args=('一次性任务',),
    # next_run_time=datetime.datetime.now() + datetime.timedelta(seconds=12))
    # scheduler.add_job(func=aps_test, args=('循环任务',), trigger='interval', seconds=3)


run_task()  # 这样当__init__.py创建app时加载这个文件，就会执行添加历史任务啦！
