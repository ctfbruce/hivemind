# comments/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import CommentForm
from .models import Comment
from posts.models import Post
from hashtags.utils import extract_hashtags
from posts.utils import notify_feed
from users.views import evaluate_recaptcha
from django.http import HttpResponse

@login_required
def add_comment(request, post_id):
    """Handle adding a new comment to a post."""
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            
            if not(evaluate_recaptcha(form)):
                return HttpResponse("bot detected . . .")
            
            new_comment = form.save(commit=False)
            new_comment.author = request.user
            new_comment.post = post
            new_comment.save()
            hashtags = extract_hashtags(new_comment.content)
            new_comment.hashtags.set(hashtags)
            notify_feed(f"{request.user.username} just commented on {post.author.username}'s post")
            return redirect('home')  # Redirect to the appropriate page
    else:
        form = CommentForm()
    return redirect("home")
