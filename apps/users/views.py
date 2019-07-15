# -*- coding: utf-8 -*-
import json

from django.contrib.auth import login, logout
from django.shortcuts import render, redirect, reverse
from django.urls import reverse
from django.views import View
# Create your views here.
from django_redis import get_redis_connection
from django.views.decorators.csrf import ensure_csrf_cookie
from users.forms import RegisterForm, LoginForm
from django.utils.decorators import method_decorator
from users.models import User
from utils.json_fun import to_json_data
from utils.res_code import Code
from . import forms


class Register(View):
    """
    /users/register
    """
    def get(self, request):
        return render(request, 'users/register.html')

    def post(self, request):
        """
        1、获取参数
        2、校验参数
        3、存入数据库
        4、返回提示
        :param request:
        :return:
        """
        json_str = request.body
        if not json_str:
            return to_json_data(errno=Code.PARAMERR, errmsg='参数为空，请重新输入')

        dict_data = json.loads(json_str.decode())

        # 校验数据
        form = RegisterForm(data=dict_data)

        if form.is_valid():

            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            mobile = form.cleaned_data.get('mobile')
            # 保存数据库，调用objects中的UserManage 中的create_user
            user = User.objects.create_user(username=username, password=password, mobile=mobile)

            login(request, user)
            return to_json_data(errno=Code.OK, errmsg='恭喜注册成功')
        else:
            # 定义错误信息列表
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))

            errmsg_str = '/'.join(err_msg_list)
            return to_json_data(errno=Code.PARAMERR, errmsg=errmsg_str)


class LoginView(View):
    """

    """
    # @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        return render(request, 'users/login.html')

    def post(self, request):
        json_str = request.body
        if not json_str:
            return to_json_data(errno=Code.PARAMERR, errmsg='参数为空，请重新输入')

        dict_data = json.loads(json_str.decode('utf8'))

        form = LoginForm(data=dict_data, request=request)

        if form.is_valid():
            return to_json_data(errmsg='登录成功')
        else:
            # 定义错误信息列表
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))

            errmsg_str = '/'.join(err_msg_list)
            return to_json_data(errno=Code.PARAMERR, errmsg=errmsg_str)


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect(reverse('news:index'))









