

from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,BooleanField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField('管理员名称', validators=[DataRequired()])
    password = StringField('管理员密码', validators=[DataRequired()])
    rememberme=BooleanField('记住我')
    submit=SubmitField('登录')


