from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Post, Comment, Tag
from django.utils.text import slugify

class UserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=True)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
    
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].help_text = None

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'profile_picture']

class PostForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        help_text="Comma-separated tags"
    )

    class Meta:
        model = Post
        fields = ["title", "content", "tags", "photo"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['tags'].initial = ', '.join([tag.name for tag in self.instance.tags.all()])
    
    def save(self, commit=True):
        post = super().save(commit=False)
        if commit:
            post.save()

        tag_names = self.cleaned_data.get("tags")
        if not tag_names:
            post.tags.clear()
        else:
            tag_list = [name.strip() for name in tag_names.split(",") if name.strip()]
            tags_to_set = []
            for name in tag_list:
                slug = slugify(name)
                tag_obj, created = Tag.objects.get_or_create(slug=slug, defaults={"name": name})
                tags_to_set.append(tag_obj)

            post.tags.set(tags_to_set)

        return post

class CommentForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Add your comment ...'}),
        required=True,
        error_messages={'required': ''}
    )

    class Meta:
        model = Comment
        fields = ["content"]

    def clean_content(self):
        content = self.cleaned_data.get("content", "")
        if len(content) < 2:
            raise forms.ValidationError("Comment is too short.")
        return content
