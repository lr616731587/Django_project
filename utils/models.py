# -*- coding: utf-8 -*-
#import numpy as np
#import pandas as pd

#pd.set_option('display.max_columns',1000)
#pd.set_option('display.width', 1000)
#pd.set_option('display.max_colwidth',1000)
#mpl.rcParams['font.sans-serif'] = [u'KaiTi']
#mpl.rcParams['axes.unicode_minus'] = False
from django.db import models


class ModelBase(models.Model):
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='逻辑删除')

    class Meta:
        abstract = True

