# posts/forms.py
from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    """Form for creating new posts."""
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
