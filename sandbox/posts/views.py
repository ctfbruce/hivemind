# posts/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from .models import Post
from .forms import PostForm
from hashtags.models import Hashtag
from comments.models import Comment  # Ensure Comment model is imported
from hashtags.utils import extract_hashtags  # If using this function
import random

@login_required
def home_view(request):
    """Display the home feed with 'Following', 'Trending', and 'Discover' tabs."""
    # Handle new post submission
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            # Parse hashtags and associate them with the post
            hashtags = extract_hashtags(new_post.content)
            new_post.hashtags.set(hashtags)
            return redirect('home')
    else:
        form = PostForm()

    # Define time threshold for trending hashtags
    time_threshold = timezone.now() - timedelta(hours=24)

    # Fetch 'Following' posts
    following_profiles = request.user.profile.following.all()
    following_posts = Post.objects.filter(author__profile__in=following_profiles)

    # Fetch 'Trending' posts (random posts from other users)
    all_users = User.objects.exclude(id=request.user.id)
    random_user_ids = all_users.values_list('id', flat=True)
    random_user_ids = list(random_user_ids)
    random.shuffle(random_user_ids)
    random_user_ids = random_user_ids[:10]
    trending_posts = Post.objects.filter(author__id__in=random_user_ids)

    # Optimize queries for posts
    prefetch_fields = [
        'hashtags',
        'comments__author',
        'comments__hashtags',
    ]
    select_fields = ['author']

    following_posts = following_posts.select_related(*select_fields).prefetch_related(*prefetch_fields).order_by('-created_at')
    trending_posts = trending_posts.select_related(*select_fields).prefetch_related(*prefetch_fields).order_by('-created_at')[:20]

    # Fetch trending hashtags
    trending_hashtags = (
        Hashtag.objects.annotate(
            recent_post_count=Count('posts', filter=Q(posts__created_at__gte=time_threshold))
        )
        .filter(recent_post_count__gt=0)
        .order_by('-recent_post_count')[:10]
    )

    # Handle search query
    query = request.GET.get('q', '')
    user_results = []
    post_results = []
    comment_results = []

    if query:
        # Search for users
        user_results = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(profile__bio__icontains=query)
        )

        # Search for posts
        post_results = Post.objects.filter(
            Q(content__icontains=query) |
            Q(author__username__icontains=query)
        ).select_related('author').prefetch_related('hashtags', 'comments')

    context = {
        'form': form,
        'following_posts': following_posts,
        'trending_posts': trending_posts,
        'trending_hashtags': trending_hashtags,
        'query': query,
        'user_results': user_results,
        'post_results': post_results,
    }
    return render(request, 'home.html', context)


@login_required
def like_post(request, post_id):
    """Allow a user to like or unlike a post."""
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    if request.method == 'POST':
        if user in post.likes.all():
            # User has already liked this post; remove the like (unlike)
            post.likes.remove(user)
        else:
            # Add a like to the post
            post.likes.add(user)

        if request.headers.get('HX-Request'):
            # If the request is an htmx request, return the updated like button partial
            context = {'post': post, 'user': user}
            html = render_to_string('posts/partials/like_button.html', context, request=request)
            return HttpResponse(html)
        else:
            # If not an htmx request, redirect back
            return redirect('home')
    else:
        return HttpResponseBadRequest('Invalid request method.')