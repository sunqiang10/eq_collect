from flask import request, session
from sqlalchemy import func
import json
from app import db
from app.models.reporter import Reporter
from app.models.user import User
from flask import jsonify
from app.models.eq_info import EqInfo
import os
from app.utils import serialize
import time
from flask import Blueprint
from flask_cors import CORS
report_blue = Blueprint("report", __name__, url_prefix="/report")
CORS(report_blue, supports_credentials=True)


# 分页查询地震数据
@report_blue.route('/ht_eq_infos', methods=['GET', 'POST'])  # 第一个参数是路由，第二个是请求方法
def ht_eq_infos():
    # recv_data = request.get_data()  # 得到前端传送的数据
    page_index = request.args.get("page_index")
    page_size = request.args.get("page_size")
    is_wx = request.args.get("is_wx")
    if session['username']:
        re_data_json = {'ok': '0', 'info': ''}
        try:
            page_total = db.session.query(func.count(EqInfo.cata_id)).scalar()
            datas = EqInfo.query.order_by(EqInfo.O_time.desc()).offset((int(page_index)-1)*int(page_size))\
                .limit(int(page_size)).all()  # 对数据做某些处理
            data_json = []
            for data in datas:
                eq_dict = serialize.serialize_model(data)
                reports = Reporter.query.order_by(Reporter.updatetime.desc()).filter_by(cata_id=data.cata_id).limit(page_size)
                report_json = []
                for report in reports:
                    if report.is_wx > int(is_wx):
                        report_dict = serialize.serialize_model(report)
                        report_dict['user'] = serialize.serialize_model(report.user)
                        report_json.append(report_dict)
                        # report_user_json = []
                        # user = User.query.filter_by(id=report.user_id).first()
                        # report_user_json.append(serialize.serialize_model(user))
                eq_dict['reports'] = report_json
                data_json.append(eq_dict)
            db.close_all_sessions()
            re_data_json['info'] = data_json
            re_data_json['page_total'] = page_total
            re_data_json["ok"] = 1
            return jsonify(re_data_json)  # 返回数据
        except Exception as e1:
            re_data_json['info'] = e1
            re_data_json["ok"] = 0
            return jsonify(re_data_json)  # 返回数据
    else:
        return ''


# 通过上报id查询上报数据
@report_blue.route('/ht_reports_by_id', methods=['GET', 'POST'])  # 第一个参数是路由，第二个是请求方法
def ht_reports_by_id():
    r_id = request.args.get("id")
    re_data_json = {'ok': '0', 'info': ''}
    if session['username']:
        try:
            report = Reporter.query.filter_by(id=int(r_id)).first()
            db.close_all_sessions()
            re_data_json['info'] = serialize.serialize_model(report)
            re_data_json["ok"] = 1
            lines = json.dumps(re_data_json, cls=serialize.DateEnconding)
            return jsonify(lines)  # 返回数据
        except Exception as e1:
            re_data_json['info'] = e1
            re_data_json["ok"] = 0
        return jsonify(re_data_json)  # 返回数据
    else:
        return ''


# 更新上报数据
@report_blue.route('/update_reports', methods=['GET', 'POST'])  # 第一个参数是路由，第二个是请求方法
def update_reports():
    ri = json.loads(request.args.get("reportInfo"))
    re_data_json = {'ok': '0', 'info': ''}
    if session['username']:
        try:
            report_new = dict_to_object(ri)
            report = Reporter.query.filter_by(id=int(report_new['id'])).first()
            if report:
                print(report.__dict__)
                for key in report_new:
                    if key == '_sa_instance_state':
                        continue
                    setattr(report, key, report_new[key])
            db.session.commit()
            db.close_all_sessions()
            re_data_json['info'] = ri
            re_data_json["ok"] = 1
            lines = json.dumps(re_data_json, cls=serialize.DateEnconding)
            return jsonify(lines)  # 返回数据
        except Exception as e1:
            re_data_json['info'] = e1
            re_data_json["ok"] = 0
        return jsonify(re_data_json)  # 返回数据
    else:
        return ''


# 通过id删除上报数据
@report_blue.route('/delete_reports', methods=['GET', 'POST'])  # 第一个参数是路由，第二个是请求方法
def delete_reports():
    r_id = json.loads(request.args.get("id"))
    re_data_json = {'ok': '0', 'info': ''}
    if session['username']:
        try:
            report = Reporter.query.filter_by(id=int(r_id)).first()
            if report:
                db.session.delete(report)
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


def dict_to_object(dictObj):
    if not isinstance(dictObj, dict):
        return dictObj
    inst = dict()
    for k,v in dictObj.items():
        inst[k] = dict_to_object(v)
    return inst


# 通过地震ID(cata_id)查询上报数据
@report_blue.route('/ht_reports_by_cata_id', methods=['GET', 'POST'])  # 第一个参数是路由，第二个是请求方法
def ht_reports_by_cata_id():
    cata_id = request.args.get("cata_id")
    is_wx = request.args.get("is_wx")
    re_data_json = {'ok': '0', 'info': ''}
    if session['username']:
        try:
            reports = Reporter.query.order_by(Reporter.updatetime.desc())\
                .filter(Reporter.cata_id == cata_id, Reporter.is_wx > int(is_wx)).limit(100)
            db.close_all_sessions()
            report_json = []
            for report in reports:
                report_json.append(serialize.serialize_model(report))
            re_data_json["ok"] = 1
            re_data_json['info'] = report_json
            return jsonify(re_data_json)  # 返回数据
        except Exception as e1:
            re_data_json['info'] = e1
            re_data_json["ok"] = 0
        return jsonify(re_data_json)  # 返回数据
    else:
        return ''


# 上传文件
@report_blue.route('/update_img', methods=['POST'])  # 第一个参数是路由，第二个是请求方法
def update_img():
    re_data_json = {'ok': '0', 'info': ''}
    if session['username']:
        try:
            if request.method == 'POST':
                # check if the post request has the file part
                if 'file' not in request.files:
                    re_data_json["info"] = 'No file part'
                file = request.files['file']
                # if user does not select file, browser also
                # submit an empty part without filename
                if file.filename == '':
                    re_data_json["info"] = 'No selected file'
                if file and allowed_file(file.filename):
                    old_filename = file.filename
                    new_filename = str(int(round(time.time() * 1000))) + '.' + old_filename.rsplit('.', 1)[1]
                    path = serialize.STATIC_FILE_PATH + 'upload' + os.sep + new_filename
                    print(path)
                    file.save(path)
                    re_data_json["info"] = '/static/upload/' + new_filename
                    re_data_json["old_filename"] = old_filename
                    re_data_json["ok"] = 1
            return jsonify(re_data_json)  # 返回数据
        except Exception as e1:
            re_data_json['info'] = e1
            re_data_json["ok"] = 0
        return jsonify(re_data_json)  # 返回数据
    else:
        return ''


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in set(['jpg', 'gif', 'png', 'jpeg', 'bmp'])


# 通过上报id查询上报数据
@report_blue.route('/ht_reports_by_open_id', methods=['GET', 'POST'])  # 第一个参数是路由，第二个是请求方法
def ht_reports_by_open_id():
    open_id = request.args.get("open_id")
    re_data_json = {'ok': '0', 'info': ''}
    if session['username']:
        try:
            result = User.query.filter(User.open_id == open_id).first()
            reports = Reporter.query.order_by(Reporter.updatetime.desc()).filter_by(user_id=int(result.id))
            report_json =[]
            for report in reports:
                eq = EqInfo.query.filter_by(cata_id=report.cata_id).first()
                report_dict = serialize.serialize_model(report)
                eq_info = serialize.serialize_model(eq)
                report_dict['eq'] = eq_info
                report_json.append(report_dict)
            db.close_all_sessions()
            re_data_json['info'] = report_json
            re_data_json["ok"] = 1
            lines = json.dumps(re_data_json, cls=serialize.DateEnconding)
            return jsonify(lines)  # 返回数据
        except Exception as e1:
            re_data_json['info'] = e1
            re_data_json["ok"] = 0
        return jsonify(re_data_json)  # 返回数据
    else:
        return ''