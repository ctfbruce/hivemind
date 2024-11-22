# hashtags/models.py

from django.db import models

class Hashtag(models.Model):
    """Model representing a hashtag."""
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"#{self.name}"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('hashtags:hashtag_detail', args=[self.name])
