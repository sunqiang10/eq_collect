from flask import render_template, flash, redirect, session, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from app.models.eq_info import EqInfo
from app.models.user import User
from app import app, db, lm, scheduler
from .forms import LoginForm
import hashlib
from flask import jsonify
import logging
import threading
import urllib.request
import os
import urllib

mylock = threading.Lock()


@app.route('/')
@app.route('/index')
@login_required
def index():
    user = g.user
    return render_template('index.html', title='Home', user=user,
                           eqInfos=EqInfo.query.order_by(EqInfo.O_time.desc()).limit(100).all())


@app.route('/eq_infos', methods=['GET', 'POST'])  # 第一个参数是路由，第二个是请求方法
def eq_infos():
    # recv_data = request.get_data()  # 得到前端传送的数据
    recv_data = request.args.get("p")
    page_index = request.args.get("page_index")
    page_size = request.args.get("page_size")
    if recv_data == '13811886617':
        datas = EqInfo.query.order_by(EqInfo.O_time.desc()).offset((int(page_index)-1)*int(page_size))\
            .limit(int(page_size)).all()  # 对数据做某些处理
        db.close_all_sessions()
        data_json = []
        re_data_json = {'ok': '0', 'info': ''}
        for data in datas:
            data_json.append(serialize(data))
        re_data_json['info'] = data_json
        re_data_json["ok"] = 1
        return jsonify(re_data_json)  # 返回数据
    else:
        return ''


def serialize(model):
    from sqlalchemy.orm import class_mapper
    columns = [c.key for c in class_mapper(model.__class__).columns]
    return dict((c, getattr(model, c)) for c in columns)


@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.before_request
def before_request():
    g.user = current_user


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
            return redirect(url_for('login'))
        if pw != user.password:
            flash('用户密码不正确.')
            return redirect(url_for('login'))
        else:
            login_user(user, remember=remember_me)
            return redirect(request.args.get('next') or url_for('index'))
    return render_template('login.html', title="Sign In", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


def create_pic():
    mylock.acquire()
    try:
        root_path = os.path.abspath(os.path.dirname(__file__)).split('eq_collect')[0]
        datas = EqInfo.query.order_by(EqInfo.O_time.desc()).limit(100).all()
        for data in datas:
            if data.is_create_pic == 0:
                file_path = root_path + 'eq_collect' + os.sep + 'static' + os.sep \
                            + 'img' + os.sep + data.Cata_id + '.png'
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


def run_task():
    scheduler.add_job(create_pic, 'cron', minute='55')
    # scheduler.add_job(create_pic, 'interval', seconds=60)
    # scheduler.add_job(func=aps_test, args=('定时任务',), trigger='cron', second='*/5')
    # scheduler.add_job(func=aps_test, args=('一次性任务',),
    # next_run_time=datetime.datetime.now() + datetime.timedelta(seconds=12))
    # scheduler.add_job(func=aps_test, args=('循环任务',), trigger='interval', seconds=3)


run_task()  # 这样当__init__.py创建app时加载这个文件，就会执行添加历史任务啦！
