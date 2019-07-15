# -*- coding: utf-8 -*-
import json
import logging
from datetime import datetime
from urllib.parse import urlencode

from django.core.paginator import Paginator, EmptyPage
from django.db.models import Count
from django.shortcuts import render

# Create your views here.
from django.views import View

from admin import constants
from news import models
from utils.json_fun import to_json_data
from utils.res_code import Code, error_map
from collections import OrderedDict
from utils import page_script


logger = logging.getLogger('django.log')


class IndexView(View):
    """
    """
    def get(self, request):

        return render(request, 'admin/index/index.html')


class TagsManageView(View):
    def get(self, request):
        tags = models.Tag.objects.values('id', 'name').annotate(num_news=Count('news')).filter(is_delete=False).\
            order_by('-num_news')

        return render(request, 'admin/news/tags_manage.html', locals())

    def post(self, request):
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map([Code.PARAMERR]))

        dict_data = json.loads(json_data.decode())

        tag_name = dict_data.get('name')
        if tag_name and tag_name.strip():
            tag_tuple = models.Tag.objects.get_or_create(name=tag_name)
            return to_json_data(errmsg='标签创建成功') if tag_tuple[-1] else to_json_data(errno=Code.DATAEXIST, errmsg='标签已存在')

        else:
            return to_json_data(errno=Code.PARAMERR, errmsg='标签名为空')

    def put(self, request, tag_id):
        json_str = request.body
        if not json_str:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])

        dict_data = json.loads(json_str.decode())
        tag_name = dict_data.get('name')
        tag = models.Tag.objects.only('id').filter(id=tag_id).first()
        if tag:
            if tag_name and tag_name.strip():
                if not models.Tag.objects.only('id').filter(name=tag_name).exists():
                    tag.name = tag_name
                    tag.save(update_fields=['name'])  # update_fields 创建一个标记
                    return to_json_data('标签更新成功')
                else:
                    return to_json_data(errno=Code.DATAEXIST, errmsg='标签名已存在')
            else:
                return to_json_data(errno=Code.PARAMERR, errmsg='标签名为空')
        else:
            return to_json_data(errno=Code.PARAMERR, errmsg='需要更新的标签不存在')

    def delete(self, request, tag_id):
        tag = models.Tag.objects.only('id').filter(id=tag_id).first()
        if tag:
            tag.delete()
            return to_json_data(errmsg='标签删除成功过')
        else:
            return to_json_data(errno=Code.PARAMERR, errmsg='标签不存在')


class HotNewsManageView(View):
    """
    id title tag_name priority
    """
    def get(self, request):
        hot_news = models.HotNews.objects.select_related('news__tag').\
            only('news_id', 'news__title', 'news__tag__name', 'priority').\
            filter(is_delete=False).order_by('priority', '-news__clicks')[0:3]

        return render(request, 'admin/news/news_hot.html', locals())


class HotNewsEditView(View):
    def delete(self, request, hotnews_id):
        hotnews = models.HotNews.objects.only('id').filter(id=hotnews_id).first()
        if hotnews:
            hotnews.is_delete = True
            hotnews.save(update_fields=['is_delete'])
            return to_json_data(errmsg='删除成功')
        else:
            return to_json_data(errno=Code.PARAMERR, errmsg='需要更新的热门新闻不存在')

    def put(self, request, hotnews_id):
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])

        dict_data = json.loads(json_data.decode())
        try:
            priority = int(dict_data.get('priority'))

            priority_list = [i for i, _ in models.HotNews.PRI_CHOICES]

            if priority not in priority_list:
                return to_json_data(errno=Code.PARAMERR, errmsg='优先级设置错误')
        except Exception as e:
            logger.info('优先级异常:\n{}'.format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg='优先级设置错误')
        hotnews = models.HotNews.objects.only('id').filter(id=hotnews_id).first()
        if not hotnews:
            return to_json_data(errno=Code.PARAMERR, errmsg='需要更新的热门文章不存在')

        if hotnews.priority == priority:
            return to_json_data(errno=Code.PARAMERR, errmsg='优先级未改变')

        hotnews.priority = priority
        hotnews.save(update_fields=['priority'])
        return to_json_data(errmsg='更新成功')


class HotNewsAddView(View):
    """
    route /admin/hotnews/add
    """
    def get(self, request):

        tags = models.Tag.objects.values('id', 'name').annotate(num_news=Count('news')).\
            filter(is_delete=False).order_by('-num_news', 'update_time')
        priority_dict = OrderedDict(models.HotNews.PRI_CHOICES)

        return render(request, 'admin/news/news_hot_add.html', locals())

    def post(self, request):
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        dict_data = json.loads(json_data)
        try:
            news_id = dict_data.get('news_id')
        except Exception as e:
            logger.info('前端传过来的文章id参数异常：\n{}'.format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg='参数错误')
        if not models.News.objects.filter(id=news_id).exists():
            return to_json_data(errno=Code.PARAMERR, errmsg='文章不存在')
        try:
            priority = int(dict_data.get('priority'))
            priority_list = [i for i, _ in models.HotNews.PRI_CHOICES]
            if priority not in priority_list:
                return to_json_data(errno=Code.PARAMERR, errmsg='热门文章的优先级设置错误')
        except Exception as e:
            logger.info('热门文章优先级异常：\n{}'.format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg='热门文章的优先级设置错误')
        hotnews_tuple = models.HotNews.objects.get_or_create(news_id=news_id)
        hotnews, is_create = hotnews_tuple
        hotnews.priority = priority
        hotnews.save(update_fields=['priority'])
        return to_json_data(errmsg="热门文章创建成功")


class NewsByTagIdView(View):
    def get(self, request, tag_id):
        newses = models.News.objects.values('id', 'title').filter(is_delete=False, tag_id=tag_id)
        news_list = [i for i in newses]
        return to_json_data(data={
            'news': news_list
        })


class NewsManageeView(View):
    def get(self, request):
        tags = models.Tag.objects.only('id', 'name').filter(is_delete=False)
        newses = models.News.objects.only('id', 'title', 'author', 'tag__name', 'update_time').\
            select_related('author', 'tag').filter(is_delete=False)
        try:
            start_time = request.GET.get('start_time', '')
            start_time = datetime.strptime(start_time, '%Y/%m/%d') if start_time else ''

            end_time = request.GET.get('end_time', '')
            end_time = datetime.strptime(end_time, '%Y/%m/%d') if end_time else ''
        except Exception as e:
            logger.info('用户输入时间有误 ：\n{}'.format(e))
            start_time = end_time = ''

        if start_time and not end_time:
            newses = newses.filter(update_time__gte=start_time)
        if end_time and not start_time:
            newses = newses.filter(update_time__lte=end_time)

        if start_time and end_time:
            newses = newses.filter(update_time__range=(start_time, end_time))

        title = request.GET.get('title', '')
        # 不忽略大小写  title__contains,
        if title:
            newses = newses.filter(title__icontains=title)

        author_name = request.GET.get('author_name', '')
        if author_name:
            newses = newses.filter(author__username__icontains=author_name)

        try:
            tag_id = request.GET.get('tag_id', 0)
        except Exception as e:
            logger.info('标签错误：\n{}'.format(e))
            tag_id = 0

        newses = newses.filter(is_delete=False, tag_id=tag_id) or newses.filter(is_delete=False)

        try:
            page = int(request.GET.get('page', 1))
        except Exception as e:
            logger.info('页码错误：\n{}'.format(e))
            page = 1

        paginator = Paginator(newses, constants.NEWS_PAGE)
        try:
            news_info = paginator.page(page)
        except EmptyPage:
            logger.info('页码大于实际页数')
            news_info = paginator.page(paginator.num_pages)

        paginator_data = page_script.get_paginator_data(paginator, news_info)

        start_time = start_time.strftime('%Y/%m/%d') if start_time else ''
        end_time = end_time.strftime('%Y/%m/%d') if end_time else ''

        context = {
            'news_info': news_info,
            'start_time': start_time,
            'end_time': end_time,
            'tags': tags,
            'paginator': paginator,
            'title': title,
            'tag_id': tag_id,
            'author_name': author_name,
            'other_param': urlencode({
                'start_time': start_time,
                'end_time': end_time,
                'title': title,
                'author_name': author_name,
                'tag_id': tag_id
            })
        }
        context.update(paginator_data)
        return render(request, 'admin/news/news_manage.html', context=context)


























