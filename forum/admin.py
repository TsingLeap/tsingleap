from django.contrib import admin

# Register your models here.
from .models import Post, Comment, Report

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('post_id', 'title', 'content', 'created_at', 'author')
    search_fields = ('title', 'content', 'author__username')
    list_filter = ('created_at', 'author__username', 'tags')
    filter_horizontal = ('tags',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('comment_id', 'content', 'created_at', 'author', 'content_object')
    search_fields = ('content', 'author__username', 'content_object__title')
    list_filter = ('created_at', 'author__username')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('report_id', 'reporter', 'reported_user', 'reported_content', 'reason', 'created_at', 'solved', 'content_object')
    search_fields = ('reporter__username', 'reported_user__username', 'reason', 'content_object__content')
    list_filter = ('created_at', 'solved', 'content_type')