# posts/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('load-more-trending-posts/', views.load_more_trending_posts, name='load_more_trending_posts'),
    path('load-more-recommended-posts/', views.load_more_recommended_posts, name='load_more_recommended_posts'),
]
