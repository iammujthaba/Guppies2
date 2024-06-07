from django import template
import re

register = template.Library()

@register.filter
def youtube_id(url):
    """
    Extracts the YouTube video ID from a URL.
    Supports both standard and short URLs.
    """
    # Updated regex pattern to support both standard and shorts URLs
    pattern = re.compile(r'(?:https?://)?(?:www\.)?(?:youtube\.com/(?:watch\?v=|shorts/)|youtu\.be/)([\w-]+)')
    match = pattern.search(url)
    return match.group(1) if match else None
