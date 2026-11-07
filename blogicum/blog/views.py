from django.shortcuts import render, get_object_or_404
from .models import Post, Category, User
from .forms import ProfileEditForm
from django.core.paginator import Paginator
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy


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


def profile_user(request, username_slug):
    template_name = 'blog/profile.html'
    profile = get_object_or_404(User, username=username_slug)
    posts = profile.posts.select_related('category', 'location', 'author')
    paginator = Paginator(posts, POSTS_LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'profile': profile,
        'page_obj': page_obj,
    }
    return render(request, template_name, context)


class PostCreateView(CreateView):
    pass


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileEditForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username_slug': self.request.user.username}
        )
