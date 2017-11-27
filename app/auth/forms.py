# -*- coding:utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(FlaskForm):
    email = StringField(u'邮件地址', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField(u'口令', validators=[DataRequired()])
    remember_me = BooleanField(u'保持登录状态')
    submit = SubmitField(u'登录')


class RegisterForm(FlaskForm):
    email = StringField(u'邮件地址', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField(u'用户名', validators=[
        DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                              'Usernames must have only letters, '
                                              'numbers,dots or underscores')
    ])
    password = PasswordField(u'密码', validators=[
        DataRequired(), EqualTo('password2', message='Password must match!')])
    password2 = PasswordField(u'确认密码', validators=[DataRequired()])
    submit = SubmitField(u'注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(), EqualTo('Confirm Password', 'Password must match!')])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Update Password')


class ResetPasswordConfirmForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(), Length(1,64), Email()
    ])
    submit = SubmitField('Confirm Change')


class ResetPasswordForm(FlaskForm):
    new_password = PasswordField('New Password', validators=[
        DataRequired(), EqualTo('confirm_password', message='Password must be matched!')
    ])
    confirm_password = PasswordField('Confirm Password')
    submit = SubmitField('Reset Password')


class ChangeEmailForm(FlaskForm):
    email = StringField('New Email', validators=[
        DataRequired(), Length(1, 64), Email()
    ])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Update Email Address')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')
