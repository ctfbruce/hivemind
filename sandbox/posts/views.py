# posts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Post
from .forms import PostForm
from django.contrib.auth.models import User
import random
from hashtags.utils import extract_hashtags

@login_required
def home_view(request):
    """Display the home feed with 'Following' and 'Trending' tabs."""
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            hashtags = extract_hashtags(new_post.content)
            new_post.hashtags.set(hashtags)
            return redirect('home')
    else:
        form = PostForm()
    # Following posts
    following_profiles = request.user.profile.following.all()
    following_posts = Post.objects.filter(author__profile__in=following_profiles).order_by('-created_at')

    # Trending posts (random posts from other users)
    all_users = User.objects.exclude(id=request.user.id)
    random_users = all_users.order_by('?')[:10]  # Randomly select 10 users
    trending_posts = Post.objects.filter(author__in=random_users).order_by('-created_at')[:20]
    
    context = {
        'form': form,
        'following_posts': following_posts,
        'trending_posts': trending_posts,
    }
    return render(request, 'home.html', context)
