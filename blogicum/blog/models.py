from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Count
from django.conf import settings
from core.constants import STR_LENGTH


User = get_user_model()


class PostQuerySet(models.QuerySet):
    """
    Этот класс создает шаблон запроса, где
    вместо self подставляется Post.objects
    """

    def published(self):
        return self.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        )

    def with_comments_count(self):
        """Счётчик комментариев на уровне БД (без N+1)"""
        return self.annotate(comment_count=Count('comments'))

    def with_related(self):
        """Подтягивает автора, категорию и местоположение одним JOIN."""
        return self.select_related('author', 'category', 'location')

    def ordered(self):
        """От новых к старым."""
        return self.order_by('-pub_date')

    def for_feed(self):
        """Готовый набор для главной/категории/чужого профиля"""
        return (
            self.published()
            .with_comments_count()
            .with_related()
            .ordered()
        )

    def for_author(self, user):
        """Все посты автора без фильтра published()"""
        return (
            self.filter(author=user)
            .with_comments_count()
            .with_related()
            .ordered()
        )


class CreatedModel(models.Model):

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено',)

    class Meta:
        abstract = True


class BaseModel(CreatedModel):
    """
    Абстрактная модель.
    Добавляет к модели атрибуты Опубликовано и Добавлено.
    """

    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.',
    )

    class Meta:
        abstract = True


class Post(BaseModel):
    title = models.CharField(max_length=STR_LENGTH, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=(
            'Если установить дату и время в будущем — '
            'можно делать отложенные публикации.'
        ),
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        related_name='posts',
    )
    location = models.ForeignKey(
        'Location',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение',
        related_name='posts',
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
        related_name='posts',
    )
    image = models.ImageField(
        'Фото',
        upload_to='post_images/',
        blank=True,
    )

    objects = PostQuerySet.as_manager()

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.title


class Category(BaseModel):
    title = models.CharField(max_length=STR_LENGTH, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text=(
            'Идентификатор страницы для URL; разрешены '
            'символы латиницы, цифры, дефис и подчёркивание.'
        ),
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(BaseModel):
    name = models.CharField(
        max_length=STR_LENGTH,
        verbose_name='Название места'
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Comment(CreatedModel):
    text = models.TextField(verbose_name='Текст')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
    )

    class Meta:
        ordering = ['created_at']
