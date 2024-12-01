from django.db.models import Count, F, ExpressionWrapper, FloatField
from datetime import timedelta
from django.utils import timezone
from .models import Post
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils.timezone import now


def get_trending_posts(limit=10, offset=0, like_weight=1, comment_weight=2):
    """
    Fetch trending posts based on a weighted engagement score (likes and comments)
    in the last 24 hours.
    
    :param limit: Number of posts to return.
    :param offset: Number of posts to skip.
    :param like_weight: Weight assigned to likes.
    :param comment_weight: Weight assigned to comments.
    :return: QuerySet of trending posts ordered by engagement score.
    """
    time_threshold = timezone.now() - timedelta(hours=24)
    
    # Annotate posts with a weighted engagement score
    trending_posts = (
        Post.objects.filter(created_at__gte=time_threshold)
        .annotate(
            num_likes=Count('likes'),
            num_comments=Count('comments'),
            engagement_score=ExpressionWrapper(
                F('num_likes') * like_weight + F('num_comments') * comment_weight,
                output_field=FloatField()
            )
        )
        .order_by('-engagement_score', '-created_at')  # Order by engagement score and recency
    )[offset:offset + limit]
    
    return trending_posts

def notify_feed(content):
    
    timestamp = now().strftime('%H:%M:%S')
    # Send the update to WebSocket clients
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'post_feed',  # Same room as in the consumer
        {
            'type': 'send_update',
            'content': content,
            'timestamp': timestamp,
        }
    )