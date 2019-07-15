import json
import logging
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger  # 分页
from django.http import Http404, HttpResponseNotFound
from django.utils.decorators import method_decorator

from Django_project import settings
from utils.json_fun import to_json_data
from utils.res_code import Code, error_map
from . import models
from django.views import View
from . import constants
from haystack.views import SearchView as _SearchView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

# Create your views here.
logger = logging.getLogger('django')


# def index(request):
#     return render(request, 'news/index.html')

# @method_decorator(cache_page(timeout=120, cache='page_cache'), name='dispatch')
class IndexView(View):
    def get(self, request):
        tags = models.Tag.objects.only('id', 'name').filter(is_delete=False)
        hot_news = models.HotNews.objects.select_related('news').only('news__title', 'news__image_url', 'news__id'). \
                       filter(is_delete=False).order_by('priority', '-news__clicks')[0:constants.HOT_NEWS_COUNT]

        return render(request, 'news/index.html', locals())  # locals参数返回前台


class NewsListView(View):
    """
    获取参数
    校验参数
    数据库拿取数据
    分页
    返回前端
    :param 必传
    tag_id:
    page:
    """

    def get(self, request):
        if not request.session:
            raise Http404
        try:
            tag_id = int(request.GET.get('tag_id', 0))
        except Exception as e:
            logger.error('标签错误\n{}'.format(e))
            tag_id = 0

        try:
            page = int(request.GET.get('page', 1))
        except Exception as e:
            logger.error('标签错误\n{}'.format(e))
            page = 1

        news_query = models.News.objects.select_related('tag', 'author').only(
            'title',
            'digest',
            'image_url',
            'update_time',
            'tag__name',
            'author__username'
        )
        news = news_query.filter(is_delete=False, tag_id=tag_id) or news_query.filter(is_delete=False)

        paginator = Paginator(news, 5)

        try:
            news_info = paginator.page(page)
        except EmptyPage:  # 页数异常
            logging.info('用户访问的页数大于总页数')
            # num_pages 返回总页数
            news_info = paginator.page(paginator.num_pages)

        news_info_list = []
        for i in news_info:
            news_info_list.append({
                'id': i.id,
                'title': i.title,
                'digest': i.digest,
                'image_url': i.image_url,
                'update_time': i.update_time.strftime('%Y年%m月%d日 %H:%M'),
                'tag_name': i.tag.name,
                'author': i.author.username,
            })

        data = {
            'total_pages': paginator.num_pages,
            'news': news_info_list,
        }

        return to_json_data(data=data)


class NewsBanner(View):
    """
    /news/banners/
    前台不需要传参
    :param
    image_url
    news__id
    news__title

    """

    def get(self, request):
        banners = models.Banner.objects.select_related('news').only(
            'image_url',
            'news__id',
            'news__title',
        ).filter(is_delete=False)[0:constants.SHOW_BANNER_COUNT]

        # 序列化输出
        banners_info_list = []
        for i in banners:
            banners_info_list.append({
                'image_url': i.image_url,
                'news_id': i.news.id,
                'news_title': i.news.title,
            })
        # 创建返回给前端的数据
        data = {
            'banners': banners_info_list
        }

        return to_json_data(data=data)


class NewsDetailView(View):
    def get(self, request, news_id):
        news = models.News.objects.select_related('tag', 'author').only(
            'title',
            'content',
            'update_time',
            'author__username',
            'tag__name',
        ).filter(is_delete=False, id=news_id).first()

        if news:
            comments = models.Comments.objects.select_related('author', 'parent'). \
                only(
                'content',
                'author__username',
                'update_time',
                'parent__content',
                'parent__author__username',
                'parent__update_time'
            ).filter(is_delete=False, news_id=news_id)

            comments_list = []
            for comm in comments:
                comments_list.append(comm.to_dict_data())

            return render(request, 'news/news_detail.html', locals())

        else:
            return HttpResponseNotFound('<h1>Page Not Found</h1>')


class NewsCommentView(View):
    """
    /news/<int:news_id>/comments/
    判断用户是否已登录
    获取参数
    校验参数
    保存数据库
    """
    def post(self, request, news_id):
        if not request.user.is_authenticated:
            return to_json_data(errno=Code.SESSIONERR, errmsg=error_map[Code.SESSIONERR])

        if not models.News.objects.only('id').filter(is_delete=False, id=news_id).exists():
            return to_json_data(errno=Code.PARAMERR, errmsg='新闻不存在')

    # 获取参数
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg='参数为空')

        dict_data = json.loads(json_data.decode('utf8'))
        # 一级评论
        content = dict_data.get('content')
        if not dict_data.get('content'):
            return to_json_data(errno=Code.PARAMERR, errmsg='评论内容不能为空')

        # 回复评论
        parent_id = dict_data.get('parent_id')
        try:
            if parent_id:
                if not models.Comments.objects.only('id').filter(is_delete=False, id=parent_id, news_id=news_id).exists():
                    return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        except Exception as e:
            logging.info('前台传的parent_id 异常： \n {}'.format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg='未知异常')

        news_content = models.Comments()
        news_content.content = content
        news_content.news_id = news_id
        news_content.author = request.user
        news_content.parent_id = parent_id if parent_id else None

        news_content.save()
        return to_json_data(data=news_content.to_dict_data())


class SearchView(_SearchView):
    # 模版文件
    template = 'news/search.html'

    # 重写响应方式，如果请求参数q为空，返回模型News的热门新闻数据，否则根据参数q搜索相关数据
    def create_response(self):
        kw = self.request.GET.get('q', '')
        if not kw:
            show_all = True
            hot_news = models.HotNews.objects.select_related('news'). \
                only('news__title', 'news__image_url', 'news__id'). \
                filter(is_delete=False).order_by('priority', '-news__clicks')

            paginator = Paginator(hot_news, settings.HAYSTACK_SEARCH_RESULTS_PER_PAGE)
            try:
                page = paginator.page(int(self.request.GET.get('page', 1)))
            except PageNotAnInteger:
                # 如果参数page的数据类型不是整型，则返回第一页数据
                page = paginator.page(1)
            except EmptyPage:
                # 用户访问的页数大于实际页数，则返回最后一页的数据
                page = paginator.page(paginator.num_pages)
            return render(self.request, self.template, locals())
        else:
            show_all = False
            qs = super(SearchView, self).create_response()
            return qs



