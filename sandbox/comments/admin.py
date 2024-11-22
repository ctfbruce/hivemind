from django.contrib import admin
from .models import Comment

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'content_excerpt', 'created_at')
    search_fields = ('author__username', 'content', 'post__content')
    list_filter = ('created_at',)

    def content_excerpt(self, obj):
        return obj.content[:50]
    content_excerpt.short_description = 'Comment Excerpt'