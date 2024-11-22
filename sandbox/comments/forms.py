
from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    """Form for creating new comments."""
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