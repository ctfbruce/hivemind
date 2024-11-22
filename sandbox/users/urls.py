# users/urls.py
from django.urls import path
from .views import register_view, login_view, logout_view, follow_view, profile_view, unfollow_view

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/<str:username>/', profile_view, name='profile'),
    path('follow/<str:username>/', follow_view, name='follow'),
    path('unfollow/<str:username>/', unfollow_view, name='unfollow'),
]
