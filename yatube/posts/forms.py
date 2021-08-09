from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["text", "group", "image"]
        labels = {
            "text": "Text",
            "group": "Group",
            "image": "Image"
        }
        help_texts = {
            "text": "Type your text here",
            "group": "Chose a group for your post",
            "image": "Add an image"
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]
        labels = {
            "text": "Comment text"
        }
        help_texts = {
            "text": "Type your comment"
        }
