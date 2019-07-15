# -*- coding: utf-8 -*-
# import numpy as np
# import pandas as pd

# pd.set_option('display.max_columns',1000)
# pd.set_option('display.width', 1000)
# pd.set_option('display.max_colwidth',1000)
# mpl.rcParams['font.sans-serif'] = [u'KaiTi']
# mpl.rcParams['axes.unicode_minus'] = False
import re

from django import forms
from django.contrib.auth import login
from django.db.models import Q
from django_redis import get_redis_connection
from users import constants
from users.models import User


class RegisterForm(forms.Form):
    username = forms.CharField(label='用户名', min_length=5, max_length=20, error_messages={'min_length': '用户名小于5位',
                                                                                         'required': '用户名不能为空'})
    password = forms.CharField(label='密码', min_length=6, max_length=20, error_messages={
        'min_length': '密码小于6位',
        'required': '密码不能为空'})
    password_repeat = forms.CharField(label='再次确认密码', min_length=6, max_length=20, error_messages={
        'min_length': '密码小于6位',
        'required': '密码不能为空'})
    mobile = forms.CharField(label='手机号', min_length=11, max_length=11, error_messages={
        'min_length': '手机号小于6位',
        'max_length': '手机号大于6位',
        'required': '手机号不能为空',
    })
    sms_code = forms.CharField(label='短信验证码', min_length=6, max_length=6, error_messages={
        'min_length': '验证码小于6位',
        'max_length': '验证码大于6位',
        'required': '验证码不能为空',
    })

    def clean_username(self):
        uname = self.cleaned_data.get('username')
        if User.objects.filter(username=uname).exists():  # exists()有数据返回True
            raise forms.ValidationError('账号已注册')
        return uname

    def clean_mobile(self):
        tel = self.cleaned_data.get('mobile')

        if not re.match(r'^1[3-9]\d{9}$', tel):
            raise forms.ValidationError('手机号格式不正确')
        if User.objects.filter(mobile=tel).exists():
            raise forms.ValidationError('手机号已注册')
        return tel

    def clean(self):
        cleaned_data = super().clean()
        passwd = cleaned_data.get('password')
        passwd_repeat = cleaned_data.get('password_repeat')

        if passwd != passwd_repeat:
            raise forms.ValidationError('两次密码不一致')
        tel = cleaned_data.get('mobile')

        sms_text = cleaned_data.get('sms_code')

        # 3 判断短信
        redis_conn = get_redis_connection(alias='verify_codes')

        sms_fmt = 'sms_{}'.format(tel).encode()

        real_sms = redis_conn.get(sms_fmt)

        if (not real_sms) or (sms_text != real_sms.decode()):
            raise forms.ValidationError('短信验证码错误')


class LoginForm(forms.Form):
    user_account = forms.CharField()
    password = forms.CharField(label='密码', min_length=6, max_length=20, error_messages={
        'min_length': '密码小于6位',
        'required': '密码不能为空'})

    # 勾选项
    remember_me = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean_user_account(self):
        user_info = self.cleaned_data.get('user_account')
        if not user_info:
            raise forms.ValidationError('用户名不能为空')
        if not re.match(r'^1[3-9]\d{9}&', user_info) and (len(user_info) < 5 or len(user_info) > 20):
            raise forms.ValidationError('格式不正确')

        return user_info

    def clean(self):
        clean_data = super().clean()
        user_info = clean_data.get('user_account')
        passwd = clean_data.get('password')
        hold_login = clean_data.get('remember_me')

        # 数据库查询
        user_queryst = User.objects.filter(Q(username=user_info) | Q(mobile=user_info))
        if user_queryst:
            user = user_queryst.first()
            if user.check_password(passwd):
                if hold_login:
                    self.request.session.set_expiry(constants.USER_SESSION_EXPIRES)
                else:
                    self.request.session.set_expiry(0)

                login(self.request, user)
            else:
                raise forms.ValidationError('密码错误')

        else:
            raise forms.ValidationError('账号错误，请重新输入')
