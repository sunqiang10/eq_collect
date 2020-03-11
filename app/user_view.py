from flask import request, session
from app import db
from sqlalchemy import func
import json
from app.models.user import User
from flask import jsonify
import hashlib
import os
import base64
from app.utils import serialize
from flask_cors import CORS
from flask import Blueprint
user_blue = Blueprint("user", __name__, url_prefix="/user")
CORS(user_blue, supports_credentials=True)


# 前端（微信端，vue端）ajax用户登录
@user_blue.route('/user_login', methods=['GET', 'POST'])  # 第一个参数是路由，第二个是请求方法
def user_login():
    # 获取客户端传参，将二进制转字符串
    re_str = request.data.decode('utf-8', 'ignore')

    form_dict = request.form.to_dict()
    keys = list(form_dict.keys())
    re_str = keys[0]

    # 将字符串转json
    j = json.loads(re_str)
    user_name = j['username']
    password = j['password']
    pw = hashlib.md5(password.encode(encoding='UTF-8')).hexdigest()
    print(pw)
    user = User.query.filter_by(username=user_name).first()
    if not user:
        return jsonify({'ok': '0', 'info': '用户名不存在！'})
    if pw != user.password:
        return jsonify({'ok': '0', 'info': '密码不正确！'})
    else:
        token = base64.b64encode(os.urandom(24)).decode('utf-8', 'ignore')
        session['user_id'] = user.id
        session['username'] = user_name
        session[user_name + '_token'] = token
        session.permanent = True
        return jsonify({'ok': '1', 'info': '登陆成功！', 'token': token})


def dict_to_object(dictObj):
    if not isinstance(dictObj, dict):
        return dictObj
    inst = dict()
    for k, v in dictObj.items():
        inst[k] = dict_to_object(v)
    return inst


# 查询用户信息
@user_blue.route('/ht_user_infos', methods=['GET', 'POST'])  # 第一个参数是路由，第二个是请求方法
def ht_user_infos():
    page_index = request.args.get("page_index")
    page_size = request.args.get("page_size")
    is_wx = request.args.get("is_wx")
    if session['username']:
        re_data_json = {'ok': '0', 'info': ''}
        try:
            page_count = db.session.query(func.count(User.id)).scalar()
            users = User.query.order_by(User.id.desc()) \
                .filter(User.is_wx == 2).offset((int(page_index) - 1) * int(page_size)) \
                .limit(int(page_size)).all()  # 对数据做某些处理
            data_json = []
            for data in users:
                user_json = serialize.serialize_model(data)
                data_json.append(user_json)
            db.close_all_sessions()
            re_data_json['info'] = data_json
            re_data_json['page_total'] = page_count
            re_data_json["ok"] = 1
            return jsonify(re_data_json)  # 返回数据
        except Exception as e1:
            re_data_json['info'] = e1
            re_data_json["ok"] = 0
            return jsonify(re_data_json)  # 返回数据
    else:
        return ''


# 后台添加用户
@user_blue.route('/ht_update_user', methods=['POST'])  # 第一个参数是路由，第二个是请求方法
def ht_update_user():
    form_dict = request.form.to_dict()
    keys = list(form_dict.keys())
    user_new = json.loads(keys[0])['params']['user_new']
    re_json = {'ok': '0', 'info': ''}
    if user_new:
        if session['username']:
            try:
                t = user_new['tel']
                is_add = 0
                if 'id' not in user_new.keys() or not isinstance(user_new['id'], int):
                    user = User.query.filter_by(tel=t).first()
                    if user:
                        re_json['info'] = "电话号码重复，该电话已经注册"
                        re_json["ok"] = 0
                        return jsonify(re_json)  # 返回数据
                    user = User()
                    pw = hashlib.md5(user_new["password"].encode(encoding='UTF-8')).hexdigest()
                    user_new["password"] = pw
                    user_new["username"] = user_new["tel"]
                    is_add = 1
                else:
                    user_tel = User.query.filter_by(tel=t).first()
                    user = User.query.filter_by(id=int(user_new['id'])).first()
                    # 修改时不能使用别人的电话
                    if not user_tel or user_tel.id == user.id:
                        is_add = 0
                        # 如果字典中有新密码则更新密码
                        if 'new_password' in user_new.keys():
                            new_password = user_new.pop('new_password')
                            pw = hashlib.md5(new_password.encode(encoding='UTF-8')).hexdigest()
                            user_new["password"] = pw
                    else:
                        re_json['info'] = "电话号码重复，该电话已经注册"
                        re_json["ok"] = 0
                        return jsonify(re_json)  # 返回数据
                if user:
                    print(user.__dict__)
                    for key in user_new:
                        if key == '_sa_instance_state':
                            continue
                        setattr(user, key, user_new[key])
                if is_add == 1:
                    db.session.add(user)

                db.session.commit()
                db.close_all_sessions()
                re_json['info'] = user_new
                re_json["ok"] = 1
                return jsonify(re_json)  # 返回数据
            except Exception as e1:
                re_json['info'] = e1
                re_json["ok"] = 0
            return jsonify(re_json)  # 返回数据
        else:
            return ''
    return jsonify(re_json)


# 通过id删除用户
@user_blue.route('/ht_delete_user', methods=['GET', 'POST'])  # 第一个参数是路由，第二个是请求方法
def ht_delete_user():
    form_dict = request.form.to_dict()
    keys = list(form_dict.keys())
    u_id = json.loads(keys[0])['params']['id']
    re_data_json = {'ok': '0', 'info': ''}
    if session['username']:
        try:
            user = User.query.filter_by(id=int(u_id)).first()
            if user:
                db.session.delete(user)
                db.session.commit()
                db.close_all_sessions()
            re_data_json["ok"] = 1
            return jsonify(re_data_json)  # 返回数据
        except Exception as e1:
            re_data_json['info'] = e1
            re_data_json["ok"] = 0
        return jsonify(re_data_json)  # 返回数据
    else:
        return ''
