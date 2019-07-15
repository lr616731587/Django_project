# -*- coding: utf-8 -*-
import os
from celery import Celery


if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'Django_project.settings'

# 创建celery实例
app = Celery('sms_code')

# 导入celery配置
app.config_from_object('celery_tasks.config')

# 自定义注册任务
app.autodiscover_tasks(['celery_tasks.sms'])








