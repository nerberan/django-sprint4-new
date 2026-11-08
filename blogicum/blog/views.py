from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Category, User
from .forms import ProfileEditForm, PostForm, CommentForm
from django.core.paginator import Paginator
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin,
)
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import Http404
from django.utils import timezone


POSTS_BY_PAGE = 10


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


# ----------Правила показа публикаций (Шаг 3). Начало----------


def index(request):
    # Выводит на главную страницу список публикаций

    template_name = 'blog/index.html'
    post_list = Post.objects.for_feed()
    paginator = Paginator(post_list, POSTS_BY_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, template_name, {'page_obj': page_obj})


def post_detail(request, id):
    # Выводит отдельую страницу публикации

    template_name = 'blog/detail.html'
    post = get_object_or_404(
        Post.objects.with_comments_count().with_related(),
        pk=id,
    )
    is_author = request.user.is_authenticated and post.author == request.user
    if not is_author:
        if (
            not post.is_published
            or not post.category.is_published
            or post.pub_date > timezone.now()
        ):
            raise Http404

    comments = post.comments.select_related('author').order_by('created_at')
    context = {
        'post': post,
        'comments': comments,
        'form': CommentForm(),
    }
    return render(request, template_name, context)


def category_posts(request, category_slug):
    # Выводит список публикаций по категориям

    template_name = 'blog/category.html'
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True,
    )
    post_list = Post.objects.for_feed().filter(category=category)
    paginator = Paginator(post_list, POSTS_BY_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))
    context = {'category': category, 'page_obj': page_obj}
    return render(request, template_name, context)


# ----------Правила показа публикаций (Шаг 3). Конец----------


# ----------Профиль (Шаг 1). Начало----------


def profile_user(request, username_slug):

    template_name = 'blog/profile.html'
    profile = get_object_or_404(User, username=username_slug)

    if request.user == profile:
        post_list = Post.objects.for_author(profile)
    else:
        post_list = Post.objects.for_feed().filter(author=profile)

    paginator = Paginator(post_list, POSTS_BY_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))
    context = {'profile': profile, 'page_obj': page_obj}
    return render(request, template_name, context)


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


# ----------Профиль (Шаг 1). Конец----------


# ----------Публикации (Шаг 2). Начало----------


class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username_slug': self.request.user.username}
        )


class PostUpdateView(OnlyAuthorMixin, LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'id': self.object.id})


class PostDeleteView(LoginRequiredMixin, OnlyAuthorMixin, DeleteView):
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username_slug': self.request.user.username}
        )


# ----------Публикации (Шаг 2). Конец----------


# ----------Коментарии (Шаг 4). Начало----------


@login_required
@require_POST
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('post:detail', pk=pk)


@login_required
@require_POST
def delete_comment(request, pk):
    pass


@login_required
@require_POST
def edit_comment(request, pk):
    pass


# ----------Коментарии (Шаг 4). Конец----------
