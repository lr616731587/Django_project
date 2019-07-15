# -*- coding: utf-8 -*-
import errno
import json
import logging

import random
import string
from utils.yuntongxun.sms import CCP
from verifications import forms
from celery_tasks.sms import task as sms_tasks
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views import View
from django_redis import get_redis_connection
from utils.captcha.captcha import captcha
from . import constants
from users.models import User
from utils.json_fun import to_json_data
from utils.res_code import Code, error_map


logger = logging.getLogger('django')
# Create your views here.


class ImageCode(View):
    def get(self, request, image_code_id):
        text, image = captcha.generate_captcha()
        print(text)
        conn_redis = get_redis_connection('verify_codes')
        conn_redis.setex('img_{}'.format(image_code_id), constants.IMAGE_CODE_REDIS_EXPIRES, text)
        logger.info('Image code {}'.format(text))
        return HttpResponse(content=image, content_type="image/jpg")


class CheckUsernameView(View):
    """
    GET usernames/(?<username>\w{5,2})/
    """
    def get(self, request, username):
        data = {
            'username': username,
            'count': User.objects.filter(username=username).count(),
        }
        return to_json_data(data=data)


class CheckMobileView(View):
    """
    Check whether the user exists
    GET usernames/(?P<username>\w{5,20})/
    """
    def get(self, request, mobile):
        data = {
            'mobile': mobile,
            'count': User.objects.filter(mobile=mobile).count(),
        }
        return to_json_data(data=data)


class SmsCodesView(View):
    """
    获取参数
    验证参数
    发送短信
    保存短信验证码
    返回前端
    POST /sms_codes/
        检查是否60s内有记录
        生成短信验证码
        保存记录
        发送短信
    """
    def post(self, request):
        json_str = request.body  # b('abc') mobile text image_code_id
        if not json_str:
            return to_json_data(errno=Code.PARAMERR, errmsg='参数为空，请重新输入')

        dict_data = json.loads(json_str.decode('utf8'))
        form = forms.CheckImgCodeForm(data=dict_data)
        #  校验参数
        if form.is_valid():
            # 获取手机号 moble

            mobile = form.cleaned_data.get('mobile')

            # 创建短信验证码
            sms_num = '%06d' % random.randint(0, 999999)

            # 将生成的短信验证内容保存到数据库
            con_redis = get_redis_connection(alias='verify_codes')
            # 创建一个60s内是否发送记录的标记
            sms_flag_fmt = 'sms_flag_{}'.format(mobile).encode('utf8')

            # 创建保存短信验证码的标记key
            sms_text_fmt = 'sms_{}'.format(mobile).encode('utf8')

            pl = con_redis.pipeline()
            try:
                pl.setex(sms_text_fmt, constants.SMS_CODE_REDIS_EXPIRES, sms_num)
                pl.setex(sms_flag_fmt, constants.SEND_SMS_CODE_INTERVAL, 1)
                # 执行redis命令
                pl.execute()
            except Exception as e:
                logger.debug('redis 执行异常:{}'.format(e))
                return to_json_data(errno=Code.UNKOWNERR, errmsg=error_map[Code.UNKOWNERR])

            # 发送短信 通知平台

            # logging.info('SMS code: {}'.format(sms_num))
            # return to_json_data(errno=Code.OK, errmsg='短信验证码发送成功')
            # celery异步发送短信
            expires = 300
            sms_tasks.send_sms_code.delay(mobile, sms_num, expires, 1)
            return to_json_data(errno=Code.OK, errmsg='短信验证码发送成功')
            # try:
            #     result = CCP().send_template_sms(mobile, [sms_num, 5], 1)
            # except Exception as e:
            #     logger.error('发送验证码短信异常[mobile:%s message: %s]' % (mobile, e))
            #     return to_json_data(errno=Code.SMSERROR, errmsg=error_map[Code.SMSERROR])
            # else:
            #     if result == 0:
            #         logger.info("发送验证码短信[正常][ mobile: %s sms_code: %s]" % (mobile, sms_num))
            #         # return to_json_data(errno=Code.OK, errmsg="短信验证码发送成功")
            #     else:
            #         logger.warning("发送验证码短信[失败][ mobile: %s ]" % mobile)
            #         return to_json_data(errno=Code.SMSFAIL, errmsg=error_map[Code.SMSFAIL])

        else:
            # 定义错误信息列表
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))

            errmsg_str = '/'.join(err_msg_list)
            return to_json_data(errno=Code.PARAMERR, errmsg=errmsg_str)

        # return HttpResponse('OK')









