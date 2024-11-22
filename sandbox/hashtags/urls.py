# hashtags/urls.py

from django.urls import path
from . import views

app_name = 'hashtags'

urlpatterns = [
    path('<str:name>/', views.hashtag_detail, name='hashtag_detail'),
]
