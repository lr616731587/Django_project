# -*- coding: utf-8 -*-
from django.shortcuts import render

from django.views import View

from course import models
# Create your views here.
from django.http import Http404
import logging
logger = logging.getLogger('django.log')


def course_list(request):
    courses = models.Course.objects.only('title', 'cover_url', 'teacher__positional_title').filter(is_delete=False)

    return render(request, 'course/course.html', locals())


class CourseDetailView(View):
    """
    <int:course_id>
    """
    def get(self, request, course_id):
        try:
            course = models.Course.objects.only('title', 'video_url', 'profile', 'outline','cover_url',
                                                'teacher__name', 'teacher__avatar_url', 'teacher__positional_title',
                                                'teacher__profile'
                                                ).select_related('teacher').filter(is_delete=False, id=course_id).first()
            return render(request, 'course/course_detail.html', locals())
        except models.Course.DoesNotExist as e:
            logger.info("当前课程出现如下异常：\n{}".format(e))
            raise Http404("此课程不存在！")
