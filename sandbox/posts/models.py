from django.db import models
from django.contrib.auth.models import User
from hashtags.models import Hashtag

class Post(models.Model):
    """Model representing a post (tweet)."""
    content = models.TextField(max_length=280)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    hashtags = models.ManyToManyField(Hashtag, blank=True, related_name='posts')
    likes = models.ManyToManyField(User, blank=True, related_name='liked_posts')

    def __str__(self):
        return f"{self.author.username}: {self.content[:50]}"
    
    def total_likes(self):
        return self.likes.count()