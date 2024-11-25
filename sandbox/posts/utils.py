# posts/utils.py

from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q
from .models import Post

def get_trending_posts(limit=10, offset=0):
    """Fetch trending posts based on likes in the last 24 hours."""
    time_threshold = timezone.now() - timedelta(hours=24)
    trending_posts = (
        Post.objects.filter(created_at__gte=time_threshold)
        .annotate(num_likes=Count('likes'))
        .order_by('-num_likes', '-created_at')
    )[offset:offset + limit]
    return trending_posts
