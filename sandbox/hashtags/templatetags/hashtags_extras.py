# hashtags/templatetags/hashtags_extras.py

from django import template
from django.utils.html import escape, urlize
from django.utils.safestring import mark_safe
import re
from django.urls import reverse

register = template.Library()

@register.filter
def link_hashtags(text):
    """Convert hashtags in text to clickable links, while escaping other HTML."""
    # First, escape the text to prevent XSS
    text = escape(text)

    # Then, replace hashtags with links
    def replace(match):
        hashtag = match.group(1)
        url = reverse('hashtags:hashtag_detail', args=[hashtag.lower()])
        link = f'<a href="{url}">#{hashtag}</a>'
        return link

    # Use raw string to avoid issues with special characters
    regex = r'#(\w+)'
    return mark_safe(re.sub(regex, replace, text))
