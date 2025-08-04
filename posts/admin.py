from django.contrib import admin
from .models import Post, Follow, Tag, Comment, AccessRequest
from django.db import models


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'author', 'tags')
    search_fields = ('title', 'content')
    prepopulated_fields = {'title': ('title',)}
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    filter_horizontal = ('tags',)

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('follower__username', 'following__username')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'created_at', 'content')
    list_filter = ('created_at', 'author', 'post')
    search_fields = ('content',)

@admin.register(AccessRequest)
class AccessRequestAdmin(admin.ModelAdmin):
    list_display = ('post', 'requester', 'status', 'requested_at', 'response_at')
    list_filter = ('status', 'requested_at')
    search_fields = ('post__title', 'requester__username')
    readonly_fields = ('requested_at', 'response_at')
    actions = ['approve_requests', 'reject_requests']

    def approve_requests(self, request, queryset):
        queryset.update(status='approved', response_at=models.DateTimeField(auto_now=True).now())
    approve_requests.short_description = "Одобрить выбранные запросы"

    def reject_requests(self, request, queryset):
        queryset.update(status='rejected', response_at=models.DateTimeField(auto_now=True).now())
    reject_requests.short_description = "Отклонить выбранные запросы"