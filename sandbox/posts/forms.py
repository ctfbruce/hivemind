# posts/forms.py

from django import forms
from .models import Post
import bleach
import html

class PostForm(forms.ModelForm):
    content = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': "What's happening?",
            'class': 'form-control',
        })
    )

    class Meta:
        model = Post
        fields = ['content']

    def clean_content(self):
        content = self.cleaned_data.get('content')
        allowed_tags = []  # No HTML tags allowed
        allowed_attributes = {}
        # Sanitize the content
        content = bleach.clean(content, tags=allowed_tags, attributes=allowed_attributes, strip=True)
        # Decode HTML entities
        content = html.unescape(content)
        
        return content
