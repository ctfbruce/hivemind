# comments/forms.py

from django import forms
from .models import Comment
import bleach

class CommentForm(forms.ModelForm):
    content = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={
            'rows': 2,
            'placeholder': "Write a comment...",
            'class': 'form-control',
        })
    )

    class Meta:
        model = Comment
        fields = ['content']

    def clean_content(self):
        content = self.cleaned_data.get('content')
        # Sanitize the content
        allowed_tags = []  # No HTML tags allowed
        allowed_attributes = {}  # No attributes allowed
        content = bleach.clean(content, tags=allowed_tags, attributes=allowed_attributes, strip=True)
        return content
