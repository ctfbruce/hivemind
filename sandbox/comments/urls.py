from django.urls import path
from . import views

app_name = 'comments'  # Namespacing the URLs

urlpatterns = [
    path('add/<int:post_id>/', views.add_comment, name='add_comment'),
]