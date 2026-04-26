from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'code_snippet', 'media', 'privacy', 'allowed_users']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'create-post-textarea',
                'placeholder': "What's on your mind? Use @username to mention someone...",
                'rows': 3,
            }),
            'code_snippet': forms.Textarea(attrs={
                'class': 'form-control',
                'style': 'font-family: monospace; font-size:.9rem;',
                'placeholder': "# Paste your code here...",
                'rows': 6,
            }),
            'media': forms.FileInput(attrs={'class': 'form-control'}),
            'privacy': forms.Select(attrs={'class': 'privacy-select', 'id': 'id_privacy'}),
            'allowed_users': forms.SelectMultiple(attrs={'class': 'form-control', 'id': 'id_allowed_users'}),
        }
