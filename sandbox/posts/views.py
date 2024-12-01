# posts/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseServerError
from django.contrib.auth.models import User
from django.utils import timezone
from django.template.loader import render_to_string
from datetime import timedelta
from .models import Post
from .forms import PostForm
from hashtags.models import Hashtag
from comments.models import Comment
from hashtags.utils import extract_hashtags
from .recommendations import recommend_posts_hybrid
from .utils import get_trending_posts, notify_feed
import random
from users.views import evaluate_recaptcha
from django.conf import settings

@login_required
def home_view(request):
    """Display the home feed with 'Following', 'Trending', and 'Discover' tabs."""
    # Handle new post submission
    if request.method == 'POST':
        return post_tweet(request)

    else:
        form = PostForm()
    # Fetch 'Following' posts
    following_profiles = request.user.profile.following.all()
    following_posts = Post.objects.filter(author__profile__in=following_profiles)

    # Fetch 'Trending' posts using the new utility function
    trending_posts = get_trending_posts(10)

    # Fetch random posts (at most 24 hours old)
    time_threshold = timezone.now() - timedelta(hours=24)
    random_posts_queryset = Post.objects.filter(created_at__gte=time_threshold)
    random_posts = list(random_posts_queryset)  # Convert to list to shuffle
    random.shuffle(random_posts)  # Shuffle the list randomly
    random_posts = random_posts[:10]  # Limit to 10 random posts

    # Optimize queries for posts
    prefetch_fields = [
        'hashtags',
        'comments__author',
        'comments__hashtags',
    ]
    select_fields = ['author']

    following_posts = following_posts.select_related(*select_fields).prefetch_related(*prefetch_fields).order_by('-created_at')
    trending_posts = trending_posts.select_related(*select_fields).prefetch_related(*prefetch_fields)

    # Fetch trending hashtags
    trending_hashtags = (
        Hashtag.objects.annotate(
            recent_post_count=Count('posts', filter=Q(posts__created_at__gte=time_threshold))
        )
        .filter(recent_post_count__gt=0)
        .order_by('-recent_post_count')[:5]
    )

    # Handle search query
    query = request.GET.get('q', '')
    user_results = []
    post_results = []

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

    # Fetch recommended posts
    recommended_posts = recommend_posts_hybrid(request.user, 10)

    context = {
        'form': form,
        'random_posts': random_posts,
        'following_posts': following_posts,
        'trending_posts': trending_posts,
        'trending_hashtags': trending_hashtags,
        'query': query,
        'user_results': user_results,
        'post_results': post_results,
        'recommended_posts': recommended_posts,
        'page': 1,
        'posts_per_page': 10,
        'recaptcha_site_key': settings.RECAPTCHA_SITE_KEY,
    }
    return render(request, 'home.html', context)


@login_required
def post_tweet(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            if not(evaluate_recaptcha(form)):
                return HttpResponse("bot detected . . .")
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            # Parse hashtags and associate them with the post
            hashtags = extract_hashtags(new_post.content)
            new_post.hashtags.set(hashtags)
            notify_feed(f"{request.user.username} just posted!")
            return redirect('home')

        else:
            return HttpResponse("Error in form")
        
    else:
        return HttpResponseServerError("some internal logic broke down")

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
            
            notify_feed(f"{user.username} liked a post <3")
            
    
    
        if request.headers.get('HX-Request'):
            # If the request is an htmx request, return the updated like button partial
            context = {'post': post, 'user': user}
            html = render_to_string('posts/partials/like_button.html', context, request=request)
            return HttpResponse(html)
        else:
            # If not an htmx request, redirect back
            return redirect('home')
    else:
        return HttpResponseBadRequest('Invalid request method.'), 


@login_required
def load_more_trending_posts(request):
    print("load more trending has been called")
    page = int(request.GET.get('page', 1))
    posts_per_page = 10
    offset = (page - 1) * posts_per_page
    trending_posts = get_trending_posts(posts_per_page, offset=offset)
    context = {
        'trending_posts': trending_posts,
        'page': page,
        'posts_per_page': posts_per_page,
    }
    return render(request, 'posts/partials/trending_post.html', context)

@login_required
def load_more_recommended_posts(request):
    print("load more recommended has been called")
    page = int(request.GET.get('page', 1))
    posts_per_page = 10
    offset = (page - 1) * posts_per_page
    recommended_posts = recommend_posts_hybrid(request.user, posts_per_page, offset=offset)
    context = {
        'recommended_posts': recommended_posts,
        'page': page,
        'posts_per_page': posts_per_page,
    }
    return render(request, 'posts/partials/recommended_post.html', context)