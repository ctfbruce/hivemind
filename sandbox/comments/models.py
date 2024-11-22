from django.db import models
from django.contrib.auth.models import User
from posts.models import Post
from hashtags.models import Hashtag

class Comment(models.Model):
    """Model representing a comment on a post."""
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments'
    )
    content = models.TextField(max_length=280)
    created_at = models.DateTimeField(auto_now_add=True)
    hashtags = models.ManyToManyField(Hashtag, blank=True, related_name='comments')

    def __str__(self):
        return f"{self.author.username} on Post {self.post.id}: {self.content[:50]}"