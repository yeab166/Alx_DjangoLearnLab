from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib import messages
from .forms import UserCreationForm, UserUpdateForm, ProfileUpdateForm, PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from .models import User, Profile, Post, Comment, Tag
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.db.models import Q
from django.http import HttpResponseForbidden


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("blog:profile", username=request.user.username)
    else:
        form = UserCreationForm()
    return render(request, "blog/register.html", {"form": form})
    

@login_required
def update_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=request.user.profile
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated!")
            return redirect("blog:profile", username=request.user.username)
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        "user_form": user_form,
        "profile_form": profile_form
    }

    return render(request, "blog/update_profile.html", context)

@login_required
def my_profile_redirect(request):
    return redirect("blog:profile", username = request.user.username)

@login_required
def profile(request, username):
    user_obj = get_object_or_404(User, username=username)
    profile = user_obj.profile
    all_posts = Post.objects.filter(author=user_obj)

    return render(request, "blog/profile.html", {"profile":profile, "posts": all_posts, "user_obj": user_obj})

class PostListView(ListView):
    model = Post
    template_name = "blog/post_list.html"  # templates/blog/post_list.html
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        queryset = Post.objects.all().order_by("-created_at")

        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(author__username__icontains=query)
            ).distinct()

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "")
        return context

# Detail page (public)
class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

# Create new post (authenticated users only)
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Post created successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse("blog:post-detail", kwargs={"pk": self.object.pk})

# Update post (only author)
class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_edit.html"

    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user
    
    def handle_no_permission(self):
        return HttpResponseForbidden("You are not allowed to edit this post.")
    
    def get_success_url(self):
        return reverse_lazy("blog:profile", kwargs={"username": self.object.author.username})

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != request.user:
            return redirect("blog:post-detail", pk=obj.pk)  # safe redirect
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Send tag names as a JS-safe string
        context['initial_tags'] = ', '.join(tag.name for tag in self.object.tags.all())
        return context

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = "blog/post_confirm_delete.html"

    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user

    def handle_no_permission(self):
        return HttpResponseForbidden("You are not allowed to delete this post.")

    def get_success_url(self):
        # After delete go to the owner's profile
        return reverse_lazy("blog:profile", kwargs={"username": self.request.user.username})


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = "blog/comment_create.html"

    def form_valid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        form.instance.post = post
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["post"] = get_object_or_404(Post, pk=self.kwargs["pk"])
        return context

    def get_success_url(self):
        return reverse("blog:post-detail", kwargs={"pk": self.kwargs['pk']})

# Edit comment
class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = "blog/comment_form.html"

    def get_success_url(self):
        # Use the comment's post pk
        return self.object.post.get_absolute_url()

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def get_success_url(self):
        return self.object.post.get_absolute_url()


# Delete comment
class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = "blog/comment_confirm_delete.html"

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def get_success_url(self):
        return self.object.post.get_absolute_url()

class PostByTagListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs['tag_slug'])
        return Post.objects.filter(tags=self.tag).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        return context
