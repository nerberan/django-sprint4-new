from django.shortcuts import render, get_object_or_404
from .models import Post, Category


POSTS_LIMIT = 5


def index(request):
    template_name = 'blog/index.html'

    post_list = (
        Post.objects.published()
        .select_related('category')
        [:POSTS_LIMIT]
    )

    context = {'post_list': post_list}
    return render(request, template_name, context)


def post_detail(request, id):
    template_name = 'blog/detail.html'

    post = get_object_or_404(
        Post.objects.published().select_related('category'), pk=id)

    context = {'post': post}
    return render(request, template_name, context)


def category_posts(request, category_slug):
    template_name = 'blog/category.html'

    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )

    post_list = Post.objects.published().filter(
        category__slug=category_slug
    ).select_related('category')

    context = {
        'category': category,
        'post_list': post_list,
    }
    return render(request, template_name, context)
