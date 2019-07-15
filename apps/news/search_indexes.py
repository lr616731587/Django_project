from haystack import indexes

from .models import News
# 模型类名+Index
class NewsIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=True)
    id = indexes.IntegerField(model_attr='id')
    title = indexes.CharField(model_attr='title')
    digest = indexes.CharField(model_attr='digest')
    content = indexes.CharField(model_attr='content')
    image_url = indexes.CharField(model_attr='image_url')

    def get_model(self):
        """
        返回建立索引的模型类
        :return:
        """
        return News

    def index_queryset(self, using=None):
        """
        返回建立索引的查询集
        :param using:
        :return:
        """
        return self.get_model().objects.filter(is_delete=False, tag_id=1)

