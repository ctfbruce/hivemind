# posts/admin.py
from django.contrib import admin
from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('author', 'content_excerpt', 'created_at')
    search_fields = ('author__username', 'content')
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    def content_excerpt(self, obj):
        return obj.content[:50]
    content_excerpt.short_description = 'Content Excerpt'
