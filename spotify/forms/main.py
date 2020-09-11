
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,SelectField,TextAreaField
from wtforms.validators import Optional,DataRequired,Email,Length



class OrderForm(FlaskForm):
    email=StringField('账号',validators=[DataRequired()])
    password=StringField('密码',validators=[DataRequired()])
    submit=SubmitField('提交')


