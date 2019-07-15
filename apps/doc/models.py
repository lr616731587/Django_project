# -*- coding: utf-8 -*-
from django.db import models
from utils.models import ModelBase

# Create your models here.


class Doc(ModelBase):
    """
    create doc model
    image_url
    title
    digest
    author
    doc_url
    """
    file_url = models.URLField(verbose_name='文件url', help_text='文件url')
    title = models.CharField(verbose_name='文档标题', max_length=150, help_text='文档标题')
    desc = models.TextField(verbose_name='文档描述', help_text='文档描述')
    image_url = models.URLField(default='', verbose_name='图片url', help_text='图片url')
    author = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)

    class Meta:
        # ordering = ['-update_time', 'id']
        db_table = 'tb_docs'
        verbose_name = '书籍'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title