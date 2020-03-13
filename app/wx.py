from flask import request, session
import urllib
import logging
import json
from app import db
from app.models.user import User
from app.models.reporter import Reporter
from flask import jsonify
import datetime
from app.models.eq_info import EqInfo
from app.models.wx_config import WxConfig
from app.utils import serialize
from flask import Blueprint
from flask_cors import CORS
import hashlib
import os
import base64
wx_blue = Blueprint("wx", __name__, url_prefix="/wx")
CORS(wx_blue, supports_credentials=True)


# 微信端访问包
@wx_blue.route('/wechat', methods=['GET', 'POST'])  # 第一个参数是路由，第二个是请求方法
def wechat():
    # recv_data = request.get_data()
    # 得到前端传送的数据

    try:
        wx_config = WxConfig.query.first()
        appid = wx_config.appid
        secret = wx_config.secret
        js_code = request.data['code']
    except Exception as e:
        logging.error(e)
        js_code = request.args.get("code")

    request_string = 'https://api.weixin.qq.com/sns/jscode2session?appid={APPID}' \
                     '&secret={SECRET}&js_code={JSCODE}&grant_type=authorization_code' \
        .format(APPID=appid, SECRET=secret, JSCODE=js_code)
    res = urllib.request.urlopen(url=request_string)
    r = json.loads(res.read().decode('utf-8'))
    if 'openid' in r:
        result = User.query.filter(User.open_id == r['openid']).first()
        if not result:
            result = User(username=r['openid'], open_id=r['openid'], is_wx='1',
                          state=datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"))
            db.session.add(result)
            db.session.commit()
        session['username'] = result.username
        r['ok'] = 1
        r['username'] = result.username
        r['nickname'] = result.nickname
        r['p_user'] = result.p_user
        r['sex'] = result.sex
        r['pic_path'] = result.pic_path
        r['is_wx'] = result.is_wx
        r['tel'] = result.tel
    return r
    db.close_all_sessions()


@wx_blue.route('/add_report', methods=['GET', 'POST'])  # 第一个参数是路由，第二个是请求方法
def add_report():
    re_son = {'ok': 0, 'info': '数据提交失败，请稍后再试'}
    try:
        if session['username']:
            js = json.loads(request.data.decode('utf-8'))
            r = js["eqReport"]
            cata_id = checkKeyValueReturnValue(r, 'cata_id')
            currenLat = checkKeyValueReturnValue(r, 'currenLat')
            currenLon = checkKeyValueReturnValue(r, 'currenLon')
            fell = checkKeyValueReturnValue(r, 'fell')
            house = checkKeyValueReturnValue(r, 'house')
            content = checkKeyValueReturnValue(r, 'content')
            open_id = checkKeyValueReturnValue(r, 'open_id')
            c_addr = checkKeyValueReturnValue(r, 'c_addr')
            death_count = checkKeyValueReturnValue(r, 'death_count')
            injured_count = checkKeyValueReturnValue(r, 'injured_count')
            wound_count = checkKeyValueReturnValue(r, 'wound_count')
            death_cause = checkKeyValueReturnValue(r, 'death_cause')
            intensity = checkKeyValueReturnValue(r, 'intensity')
            pic_path = checkKeyValueReturnValue(r, 'pic_path')
            old_pic_path = checkKeyValueReturnValue(r, 'old_pic_path')
            house_type = checkKeyValueReturnValue(r, 'house_type')
            is_wx = checkKeyValueReturnValue(r, 'is_wx')
            if open_id == "":
                re_son['ok'] = 0
                re_son['info'] = '登录超时，请重新打开小程序'
                return re_son
            user = User.query.filter(User.open_id == open_id).first()
            if cata_id == '':
                re_son['ok'] = 0
                re_son['info'] = '震情为空，请重新进入小程序'
                return re_son
            arricle = Reporter(
                cata_id=cata_id
                , currenLat=currenLat
                , currenLon=currenLon
                , fell=fell
                , house=house
                , content=content
                , open_id=open_id
                , user_id=user.id
                , c_addr=c_addr
                , death_count=death_count
                , injured_count=injured_count
                , wound_count=wound_count
                , death_cause=death_cause
                , intensity=intensity
                , pic_path=pic_path
                , old_pic_path=old_pic_path
                , house_type=house_type
                , is_wx=is_wx
                , updatetime=datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"))
            db.session.add(arricle)
            db.session.commit()
            db.session.remove()
            re_son['ok'] = 1
            re_son['info'] = '提交成功'
            db.close_all_sessions()
        else:
            re_son['ok'] = 0
            re_son['info'] = '登录超时或者未登陆，请重新登陆'
    except Exception as e:
        logging.error(e)
    return re_son


@wx_blue.route('/eq_reports', methods=['GET', 'POST'])
def eq_reports():
    data_json = []
    re_data_json = {'ok': '0', 'info': ''}
    if session['username']:
        cata_id = request.args.get("cata_id")
        datas = Reporter.query.order_by(Reporter.updatetime.desc())\
            .filter_by(cata_id=cata_id).limit(100)
        for data in datas:
            report_dict = serialize.serialize_model(data)
            user = User.query.filter_by(id=data.user_id).first()
            user_dict = serialize.serialize_model(user)
            user_dict.pop("password")
            report_dict['user'] = user_dict
            data_json.append(report_dict)
        re_data_json['info'] = data_json
        re_data_json["ok"] = 1
    else:
        re_data_json['ok'] = 0
        re_data_json['info'] = '登录超时或者未登陆，请重新登陆'
    return jsonify(re_data_json)  # 返回数据


@wx_blue.route('/eq_infos', methods=['GET', 'POST'])  # 第一个参数是路由，第二个是请求方法
def eq_infos():
    # recv_data = request.get_data()  # 得到前端传送的数据
    page_index = request.args.get("page_index")
    page_size = request.args.get("page_size")
    if session['username']:
        datas = EqInfo.query.order_by(EqInfo.O_time.desc()).offset((int(page_index)-1)*int(page_size))\
            .limit(int(page_size)).all()  # 对数据做某些处理
        db.close_all_sessions()
        data_json = []
        re_data_json = {'ok': '0', 'info': ''}
        for data in datas:
            data_json.append(serialize.serialize_model(data))
        re_data_json['info'] = data_json
        re_data_json["ok"] = 1
        lines = json.dumps(re_data_json, cls=serialize.DateEnconding)
        return jsonify(lines)  # 返回数据
    else:
        return ''


# 绑定微信帐号
@wx_blue.route('/wx_login', methods=['GET', 'POST'])  # 第一个参数是路由，第二个是请求方法
def wx_login():
    # 获取客户端传参，将二进制转字符串
    r = json.loads(request.data.decode('utf-8'))
    re_data_json = {'ok': '0', 'info': ''}
    user_name = r['username']
    password = r['password']
    open_id = r['open_id']
    if (not user_name) or user_name == '' or user_name.strip() == '':
        re_data_json = {'ok': '0', 'info': '用户名不能为空'}
        return jsonify(re_data_json)
    if (not password) or password == '' or password.strip() == '':
        re_data_json = {'ok': '0', 'info': '密码不能为空'}
        return jsonify(re_data_json)
    if open_id.strip() == '':
        re_data_json = {'ok': '0', 'info': '小程序超时，请重新打开小程序'}
        return jsonify(re_data_json)
    pw = password
    user = User.query.filter_by(username=user_name).first()
    if not user:
        return jsonify({'ok': '0', 'info': '用户名不存在！'})
    if pw != user.password:
        return jsonify({'ok': '0', 'info': '密码不正确！'})
    else:
        result = User.query.filter(User.username == open_id).first()
        if result:
            # 如果用户id 相同 为同一条记录 否则保留 user 删除 result
            if user.id != result.id:
                user.open_id = open_id
                db.session.delete(result)
        else:
            user.open_id = open_id
        db.session.commit()
        token = base64.b64encode(os.urandom(24)).decode('utf-8', 'ignore')
        session['user_id'] = user.id
        session['username'] = user_name
        session[user_name + '_token'] = token
        session.permanent = True
        re_data_json = {'ok': '1', 'info': '登陆成功',
                        'token': token,
                        'username': user.username,
                        'nickname': user.nickname,
                        'sex': user.sex,
                        'p_user': user.p_user,
                        'pic_path': user.pic_path,
                        'is_wx': user.is_wx,
                        'tel': user.tel}
        db.close_all_sessions()
        return jsonify(re_data_json)

    return jsonify(re_data_json)


def checkKeyValueReturnValue(d, k):
    if k in d.keys():
        return d[k]
    else:
        return ""


# 微信用户授权
@wx_blue.route('/login4wx', methods=['GET', 'POST'])  # 第一个参数是路由，第二个是请求方法
def login4wx():
    # 获取客户端传参，将二进制转字符串
    r = json.loads(request.data.decode('utf-8'))
    re_data_json = {'ok': '0', 'info': ''}
    nickname = ''
    pic_path = ''
    sex = ''
    province = ''
    city = ''
    open_id = ''
    if 'nickname' in r:
        nickname = r['nickname']
    if 'pic_path' in r:
        pic_path = r['pic_path']
    if 'sex' in r:
        sex = r['sex']
    if 'province' in r:
        province = r['province']
    if 'city' in r:
        city = r['city']
    if 'open_id' in r:
        open_id = r['open_id']
    if open_id.strip() == '':
        re_data_json = {'ok': '0', 'info': '小程序超时，请重新打开小程序'}
        return jsonify(re_data_json)

    user = User.query.filter_by(open_id=open_id).first()
    if not user:
        return jsonify({'ok': '0', 'info': '用户不存在！'})
    else:
        user.sex = sex
        try:
            user.nickname = nickname
            user.pic_path = pic_path
            user.province = province
            user.city = city
        except Exception as e1:
            print(e1)
        db.session.commit()

        token = base64.b64encode(os.urandom(24)).decode('utf-8', 'ignore')
        session['user_id'] = user.id
        session['username'] = user.username
        session[user.username + '_token'] = token
        re_data_json = {'ok': '1', 'info': '登陆成功', 'token': token,
                        'username': user.username,
                        'nickname': user.nickname,
                        'sex': user.sex,
                        'p_user': user.p_user,
                        'pic_path': user.pic_path,
                        'is_wx': user.is_wx,
                        'tel': user.tel}
        db.close_all_sessions()
        return jsonify(re_data_json)

    return jsonify(re_data_json)