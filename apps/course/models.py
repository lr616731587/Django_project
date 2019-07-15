# -*- coding: utf-8 -*-
from django.db import models
from utils.models import ModelBase
# Create your models here.


class Teacher(ModelBase):
    name = models.CharField(max_length=150, verbose_name='讲师姓名', help_text='讲师姓名')
    positional_title = models.CharField(max_length=150, verbose_name='职称', help_text='职称')
    profile = models.TextField(verbose_name='简介', help_text='简介')
    avatar_url = models.URLField(default='', verbose_name='头像url', help_text='头像url')

    class Meta:
        db_table = 'tb_teachers'
        verbose_name = '讲师'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class CourseCategory(ModelBase):
    name = models.CharField(max_length=100, verbose_name='课程分类', help_text='课程分类')

    class Meta:
        db_table = 'tb_course_category'
        verbose_name = '课程分类'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Course(ModelBase):
    title = models.CharField(max_length=150, verbose_name='课程名', help_text='课程名')
    cover_url = models.URLField(verbose_name='课程封面图片', help_text='课程封面图片')
    video_url = models.URLField(verbose_name='课程视频URL', help_text='课程视频URL')
    duration = models.FloatField(default=0.0, verbose_name='课程时长', help_text='课程时长')
    profile = models.TextField(null=True, blank=True, verbose_name='课程简介', help_text='课程简介')
    outline = models.TextField(null=True, blank=True, verbose_name='课程大纲', help_text='课程大纲')
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(CourseCategory, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'tb_course'
        verbose_name = '课程'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title

