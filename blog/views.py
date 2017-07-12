from django.shortcuts import render, get_object_or_404
from .models import Post, Category
import markdown
from comments.forms import CommentForm
from markdown.extensions.toc import TocExtension
from django.utils.text import slugify
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.
def index(request):
    post_list = Post.objects.all().order_by('-created_time')
    paginator = Paginator(post_list, 10)
    page = request.GET.get('page')

    try:
        post_list = paginator.page(page)
    except PageNotAnInteger:
        post_list = paginator.page(1)
    except EmptyPage:
        post_list = paginator.page(paginator.num_pages)
    return render(request, 'blog/index.html', context={
        'post_list': post_list,
    })

# class IndexView(ListView):
#     model = Post
#     template_name = 'blog/index.html'
#     context_object_name = 'post_list'
#     paginate_by = 10



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