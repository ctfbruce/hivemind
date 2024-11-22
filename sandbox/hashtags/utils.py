# hashtags/utils.py

import re
from .models import Hashtag

def extract_hashtags(text):
    """Extract hashtags from text and return a list of Hashtag objects."""
    hashtag_names = set(part[1:] for part in text.split() if part.startswith('#'))
    hashtags = []
    for name in hashtag_names:
        hashtag, created = Hashtag.objects.get_or_create(name=name.lower())
        hashtags.append(hashtag)
    return hashtags
