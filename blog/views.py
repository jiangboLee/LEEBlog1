from django.shortcuts import render, get_object_or_404
from .models import Post, Category
import markdown
from comments.forms import CommentForm
from markdown.extensions.toc import TocExtension
from django.utils.text import slugify
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic.list import ListView

# Create your views here.
# def index(request):
#     post_list = Post.objects.all().order_by('-created_time')
#     paginator = Paginator(post_list, 10)
#     page = request.GET.get('page')
#
#     try:
#         post_list = paginator.page(page)
#     except PageNotAnInteger:
#         post_list = paginator.page(1)
#     except EmptyPage:
#         post_list = paginator.page(paginator.num_pages)
#     return render(request, 'blog/index.html', context={
#         'post_list': post_list,
#     })

class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = 1
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = context.get('paginator')
        page = context.get('page_obj')
        is_paginator = context.get('is_paginated')
        # 调用自己写的 pagination_data 方法获得显示分页导航条需要的数据
        paginator_date = self.pagination_data(paginator, page, is_paginator)
        # 将分页导航条的模板变量更新到 context 中
        context.update(paginator_date)
        return context

    def pagination_data(self, paginator, page, is_paginated):
        if not is_paginated:
            return {}
        left = []
        right = []
        left_has_more = False
        right_has_more = False
        first = False
        last = False
        # 获得用户当前请求的页码号
        page_number = page.number
        # 获得分页后的总页数
        total_pages = paginator.num_pages
        page_range = paginator.page_range

        if page_number == 1:
            # 这里只获取了当前页码后连续两个页码，你可以更改这个数字以获取更多页码。
            right = page_range[page_number: page_number + 2];
            if right[-1] < total_pages - 1:
                right_has_more = True
            if right[-1] < total_pages:
                last = True
        elif page_number == total_pages:
            left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:page_number -1]
            if left[0] > 2:
                left_has_more = True
            if left[0] > 1:
                first = True
        else:
            left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:page_number -1]
            right = page_range[page_number:page_number + 2]
            if right[-1] < total_pages - 1:
                right_has_more = True
            if right[-1] < total_pages:
                last = True
            if left[0] > 2:
                left_has_more = True
            if left[0] > 1:
                first = True
        context = {
            'left': left,
            'right': right,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more,
            'first': first,
            'last': last,
        }
        return  context



def detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    md = markdown.Markdown(extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        TocExtension(slugify=slugify)
    ])
    post.body = md.convert(post.body)
    form = CommentForm()
    comment_list = post.comment_set.all()
    context = {
        'post': post,
        'form': form,
        'comment_list': comment_list,
        'toc': md.toc,
    }
    return render(request, 'blog/detail.html', context=context)

def archives(request, year, month):
    post_list = Post.objects.filter(created_time__year=year,
                                    created_time__month=month).order_by('-created_time')
    return render(request, 'blog/index.html', context={
        'post_list': post_list,
    })

def category(request, pk):
    cate = get_object_or_404(Category, pk=pk)
    post_list = Post.objects.filter(category=cate).order_by('-created_time')
    return render(request, 'blog/index.html', context={
        'post_list': post_list,
    })

def search(request):
    li = request.GET.get('li')
    error_msg = ''
    if not li:
        error_msg = '请输入关键字'
        return render(request, 'blog/index.html', {'error_msg': error_msg})

    post_list = Post.objects.filter(title__icontains=li)
    return render(request, 'blog/index.html', {
        'error_msg': error_msg,
        'post_list': post_list,
    })