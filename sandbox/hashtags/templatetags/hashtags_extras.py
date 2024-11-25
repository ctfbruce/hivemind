from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe
import re
from django.urls import reverse
import html

register = template.Library()

@register.filter
def link_hashtags(text):
    """
    Convert hashtags in text to clickable links, while escaping other HTML.
    Ensure single quotes remain unescaped.
    """
    # Escape the text to handle potentially unsafe HTML
    escaped_text = escape(text)

    # Decode single quotes to avoid escaping them
    escaped_text = escaped_text.replace("&#x27;", "'")

    # Regex pattern to find hashtags
    hashtag_regex = r'#(\w+)'

    # Function to replace hashtags with links
    def replace(match):
        hashtag = match.group(1)
        url = reverse('hashtags:hashtag_detail', args=[hashtag.lower()])
        return f'<a href="{url}">#{hashtag}</a>'

    # Replace hashtags with links
    linked_text = re.sub(hashtag_regex, replace, escaped_text)

    # Mark the resulting text as safe for rendering
    return mark_safe(linked_text)
