from django.urls import path
from . import views


app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path(
        'posts/create/',
        views.PostCreateView.as_view(),
        name='create_post'
    ),
    path(
        'posts/<int:id>/',
        views.post_detail,
        name='post_detail'
    ),
    path(
        'category/<slug:category_slug>/',
        views.category_posts,
        name='category_posts'
    ),
    path(
        'profile/edit/',
        views.ProfileUpdateView.as_view(),
        name='edit_profile'
    ),
    path(
        'profile/<slug:username_slug>/',
        views.profile_user,
        name='profile'
    ),
    path(
        'posts/<int:id>/edit/',
        views.PostUpdateView.as_view(),
        name='post_edit'
    ),
    path(
        'posts/<int:id>/delete/',
        views.PostDeleteView.as_view(),
        name='post_delete'
    ),
]
