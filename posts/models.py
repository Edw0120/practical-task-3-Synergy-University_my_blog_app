from django.db import models
from django.contrib.auth.models import User

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Название тега")

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ['name']

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержимое")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    STATUS_CHOICES = [
        ('public', 'Публичный'),
        ('hidden_request', 'Скрытый (по запросу)'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='public', verbose_name="Статус")
    tags = models.ManyToManyField(Tag, blank=True, verbose_name="Теги")

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='following_set', on_delete=models.CASCADE, verbose_name="Подписчик")
    following = models.ForeignKey(User, related_name='follower_set', on_delete=models.CASCADE, verbose_name="Подписан на")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата подписки")

    class Meta:
        unique_together = ('follower', 'following')
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return f"{self.follower.username} подписан на {self.following.username}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name="Пост")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")
    content = models.TextField(verbose_name="Содержимое комментария")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ['created_at']

    def __str__(self):
        return f"Комментарий от {self.author.username} к посту '{self.post.title[:30]}...'"


class AccessRequest(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name="Пост")
    requester = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Запрашивающий")
    STATUS_CHOICES = [
        ('pending', 'Ожидает рассмотрения'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус запроса")
    requested_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата запроса")
    response_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата ответа")

    class Meta:
        unique_together = ('post', 'requester')
        verbose_name = "Запрос на доступ"
        verbose_name_plural = "Запросы на доступ"
        ordering = ['-requested_at']

    def __str__(self):
        return f"Запрос от {self.requester.username} на доступ к '{self.post.title}' - {self.get_status_display()}"