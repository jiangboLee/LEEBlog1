from django.contrib.syndication.views import Feed
from .models import Post

class AllPostsRssFeed(Feed):
    title = "LEE 博客"
    link = "http://www.ljb.space/"
    description = "LEE 博客演示测试文章"
    def items(self):
        return Post.objects.all()
    def item_title(self, item):
        return '[%s] %s' % (item.category, item.title)
    def item_description(self, item):
        return item.body