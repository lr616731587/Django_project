# -*- coding: utf-8 -*-
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import render
from django.views import View
import requests

from utils.json_fun import to_json_data
from utils.res_code import Code, error_map
from .models import Doc
from django.conf import settings

import logging
from django.utils.encoding import escape_uri_path
logger = logging.getLogger('django.log')
# Create your views here.


def doc_index(request):
    docs = Doc.objects.defer('author', 'create_time', 'update_time', 'is_delete').filter(is_delete=False)
    return render(request, 'doc/docDownload.html', locals())


class DocDownload(View):
    """
    /doc/<int:doc_id>/
    """
    def get(self, request, doc_id):
        if not request.user.is_authenticated:
            return render(request, 'users/login.html')

        if not request.user.is_superuser:
            return HttpResponse('不是vip')

        doc = Doc.objects.only('file_url').filter(is_delete=False, id=doc_id).first()
        if doc:
            doc_url = doc.file_url
            doc_url = settings.SITE_DOMAIN_PORT + doc_url
            try:
                res = FileResponse(requests.get(doc_url, stream=True))
            except Exception as e:
                logger.info('获取文件内容异常: \n{}'.format(e))
                raise Http404

            ex_name = doc_url.split('.')[-1]

            if not ex_name:
                raise Http404('文档url异常')

            else:
                ex_name = ex_name.lower()

            if ex_name == 'pdf':
                res["Content-type"] = 'application/pdf'
            elif ex_name == "zip":
                res["Content-type"] = "application/zip"
            elif ex_name == "doc":
                res["Content-type"] = "application/msword"
            elif ex_name == "xls":
                res["Content-type"] = "application/vnd.ms-excel"
            elif ex_name == "docx":
                res["Content-type"] = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            elif ex_name == "ppt":
                res["Content-type"] = "application/vnd.ms-powerpoint"
            elif ex_name == "pptx":
                res["Content-type"] = "application/vnd.openxmlformats-officedocument.presentationml.presentation"

            else:
                raise Http404('文档格式错误')

            # 流畅的python.pdf
            doc_filename = escape_uri_path(doc_url.split('/')[-1])

            res['Content-Disposition'] = "attachment; filename*=UTF-8''{}".format(doc_filename)
            return res

        else:
            raise Http404('文档不存在')



