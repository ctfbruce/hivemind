from django.db.models import Count, Q
from django.contrib.auth.models import User
from .models import Post
from hashtags.models import Hashtag
def recommend_posts_content_based(user, num_recommendations=10):
    # Get the tags from the posts the user has liked
    liked_tags = Hashtag.objects.filter(posts__likes=user).distinct()

    # Find other posts with these tags that the user hasn't liked yet
    similar_posts = Post.objects.filter(
        hashtags__in=liked_tags
    ).exclude(
        likes=user
    ).annotate(
        common_tag_count=Count('hashtags')
    ).order_by('-common_tag_count', '-created_at').distinct()[:num_recommendations]

    return similar_posts

def recommend_posts_from_similar_users(user, num_similar_users=50, num_recommendations=10):
    # Get posts liked by the user
    user_liked_posts = Post.objects.filter(likes=user)

    # Find users who have liked the same posts
    similar_users = User.objects.filter(
        liked_posts__in=user_liked_posts
    ).exclude(
        id=user.id
    ).annotate(
        similarity_score=Count('liked_posts')
    ).order_by('-similarity_score')[:num_similar_users]

    # Get posts liked by similar users that the current user hasn't liked
    similar_users_posts = Post.objects.filter(
        likes__in=similar_users
    ).exclude(
        likes=user
    ).annotate(
        like_count=Count('likes')
    ).order_by('-like_count', '-created_at').distinct()[:num_recommendations]

    return similar_users_posts

def recommend_posts_hybrid(user, num_recommendations=10):
    # Get recommendations from both methods

    
    content_based_posts = recommend_posts_content_based(user, num_recommendations * 2)
    collaborative_posts = recommend_posts_from_similar_users(user, num_similar_users=50, num_recommendations=num_recommendations * 2)


    # Combine the QuerySets
    combined_posts = (content_based_posts | collaborative_posts).distinct()

    # Annotate posts with a score (you can adjust weights here)
    combined_posts = combined_posts.annotate(
        score=Count('likes') + Count('hashtags')
    )

    # Order the combined posts by score, likes, and recency
    recommended_posts = combined_posts.order_by('-score', '-likes', '-created_at')[:num_recommendations]

    return recommended_posts
