from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    # 域初始化时，第一个参数是设置label属性的
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我', default=False)
