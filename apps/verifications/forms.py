# -*- coding: utf-8 -*-
from django import forms
from users.models import User
from django.core.validators import RegexValidator
from django_redis import get_redis_connection

# 创建手机号正则校验器

mobile_validator = RegexValidator(r'^1[3-9]\d{9}$', '手机号码格式错误')


class CheckImgCodeForm(forms.Form):
    mobile = forms.CharField(max_length=11, min_length=11,validators=[mobile_validator, ],
                             error_messages={'min_length': '手机号长度错误', 'max_length': '手机号长度有误', 'required': '手机号不能为空'})

    image_code_id = forms.UUIDField(error_messages={'required': '图片uuid不能为空'})
    text = forms.CharField(max_length=4, min_length=4, error_messages={
        'min_lenght': '验证码长度错误',
        'max_lenght': '验证码长度错误',
        'required': '验证码不能为空'
    })

    def clean(self):
        cleaned_data = super().clean()
        mobile_num = cleaned_data.get('mobile')
        image_uuid = cleaned_data.get('image_code_id')
        image_text = cleaned_data.get('text')

        if User.objects.filter(mobile=mobile_num).count():
            raise forms.ValidationError('手机号已注册')

    # 获取图片验证码
        try:
            con_redis = get_redis_connection(alias='verify_codes')
        except Exception as e:
            raise forms.ValidationError('未知错误')
        img_key = 'img_{}'.format(image_uuid).encode()
        real_image_code_origin = con_redis.get(img_key)  # b'abc
        real_image_code = real_image_code_origin.decode('utf8') if real_image_code_origin else None
        con_redis.delete(img_key)
        print(real_image_code_origin)
        # 判断用户输入的图片验证码和数据库里取得的是否一致
        if (not real_image_code) or (image_text.upper() != real_image_code):
            raise forms.ValidationError('图片验证码失败')

        sms_flag_fmt = 'sms_flag_{}'.format(mobile_num).encode()
        sms_flag = con_redis.get(sms_flag_fmt)
        if sms_flag:
            raise forms.ValidationError('获取短信验证码过于频繁')
























