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
from app.utils import serialize
from flask import Blueprint
from flask_cors import CORS
wx_blue = Blueprint("wx", __name__, url_prefix="/wx")
CORS(wx_blue, supports_credentials=True)


# 微信端访问包
@wx_blue.route('/wechat', methods=['GET', 'POST'])  # 第一个参数是路由，第二个是请求方法
def wechat():
    # recv_data = request.get_data()
    # 得到前端传送的数据
    appid = ''
    secret = ''
    try:
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
        result = User.query.filter(User.username == r['openid']).first()
        if not result:
            result = User(username=r['openid'], state=datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"))
            db.session.add(result)
            db.session.commit()
            db.session.remove()
        session['username'] = result.username
    return r


@wx_blue.route('/add_report', methods=['GET', 'POST'])  # 第一个参数是路由，第二个是请求方法
def add_report():
    re_son = {'ok': 0, 'info': '数据提交失败，请稍后再试'}
    try:
        if session['username']:
            r = json.loads(request.data.decode('utf-8'))
            cata_id = r['cata_id']
            currenLat = r['currenLat']
            currenLon = r['currenLon']
            fell = r['fell']
            house = r['house']
            person = r['person']
            content = r['content']
            open_id = r['open_id']
            c_addr = r['c_addr']
            arricle = Reporter(
                cata_id=cata_id
                , currenLat=currenLat
                , currenLon=currenLon
                , fell=fell
                , house=house
                , person=person
                , content=content
                , open_id=open_id
                , c_addr=c_addr
                , updatetime=datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"))
            db.session.add(arricle)
            db.session.commit()
            db.session.remove()
            re_son['ok'] = 1
            re_son['info'] = '提交成功'
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
            data_json.append(serialize.serialize_model(data))
        re_data_json['info'] = data_json
        re_data_json["ok"] = 1
    else:
        re_data_json['ok'] = 0
        re_data_json['info'] = '登录超时或者未登陆，请重新登陆'
    return jsonify(re_data_json)  # 返回数据


@wx_blue.route('/eq_infos', methods=['GET', 'POST'])  # 第一个参数是路由，第二个是请求方法
def eq_infos():
    # recv_data = request.get_data()  # 得到前端传送的数据
    recv_data = request.args.get("p")
    page_index = request.args.get("page_index")
    page_size = request.args.get("page_size")
    if recv_data == '13811886617' and session['username']:
        datas = EqInfo.query.order_by(EqInfo.O_time.desc()).offset((int(page_index)-1)*int(page_size))\
            .limit(int(page_size)).all()  # 对数据做某些处理
        db.close_all_sessions()
        data_json = []
        re_data_json = {'ok': '0', 'info': ''}
        for data in datas:
            data_json.append(serialize.serialize_model(data))
        re_data_json['info'] = data_json
        re_data_json["ok"] = 1
        return jsonify(re_data_json)  # 返回数据
    else:
        return ''


