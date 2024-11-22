from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    """Model representing a post (tweet)."""
    content = models.TextField(max_length=280)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username}: {self.content[:50]}"