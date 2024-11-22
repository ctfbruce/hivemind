# hashtags/views.py

from django.shortcuts import render, get_object_or_404
from .models import Hashtag
from posts.models import Post

def hashtag_detail(request, name):
    """Display posts associated with a hashtag."""
    hashtag = get_object_or_404(Hashtag, name=name.lower())
    posts = Post.objects.filter(hashtags=hashtag).order_by('-created_at')
    context = {
        'hashtag': hashtag,
        'posts': posts,
    }
    return render(request, 'hashtags/hashtag_detail.html', context)
