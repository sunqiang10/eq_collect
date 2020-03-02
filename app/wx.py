from flask import request
from app import app, db, views
import urllib
import logging
import json
from app.models.user import User
from app.models.reporter import Reporter
from flask import jsonify
import datetime


@app.route('/wechat', methods=['GET', 'POST'])  # 第一个参数是路由，第二个是请求方法
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
            arricle = User(username=r['openid'], state=datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"))
            db.session.add(arricle)
            db.session.commit()
            db.session.remove()
    return r


@app.route('/add_report', methods=['GET', 'POST'])  # 第一个参数是路由，第二个是请求方法
def add_report():
    re_son = {'ok': 0, 'info': '数据提交失败，请稍后再试'}
    try:
        r = json.loads(request.data.decode('utf-8'))
        Cata_id = r['Cata_id']
        currenLat = r['currenLat']
        currenLon = r['currenLon']
        fell = r['fell']
        house = r['house']
        person = r['person']
        content = r['content']
        open_id = r['open_id']
        c_addr = r['c_addr']
        arricle = Reporter(
            Cata_id=Cata_id
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
    except Exception as e:
        logging.error(e)
    return re_son


@app.route('/eq_reports', methods=['GET', 'POST'])
def eq_reports():
    Cata_id = request.args.get("Cata_id")
    datas = Reporter.query.order_by(Reporter.updatetime.desc())\
        .filter_by(Cata_id=Cata_id).limit(100)
    data_json = []
    re_data_json = {'ok': '0', 'info': ''}
    for data in datas:
        data_json.append(views.serialize(data))
    re_data_json['info'] = data_json
    re_data_json["ok"] = 1
    return jsonify(re_data_json)  # 返回数据

