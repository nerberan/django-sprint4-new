from django import forms
from .models import User, Post


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            "title",
            "text",
            "pub_date",
            "category",
            "location",
            "image",
        )
        widgets = {
            "post": forms.DateInput(
                format="%Y-%m-%d",
                attrs={"type": "date"},
            ),
        }
