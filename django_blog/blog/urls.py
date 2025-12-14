from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = "blog"

urlpatterns = [
    path("register/", views.register, name="register"),
    path("accounts/profile/", views.my_profile_redirect, name="my-profile"),
    path("accounts/profile/<str:username>/", views.profile, name="profile"),
    path("accounts/update_profile/", views.update_profile, name="update_profile"),
    path("login/", auth_views.LoginView.as_view(template_name="blog/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page='blog:login'), name="logout"),
    path("post/", views.PostListView.as_view(), name="post-list"),
    path("post/new/", views.PostCreateView.as_view(), name="post-create"),
    path("post/<int:pk>/", views.PostDetailView.as_view(), name="post-detail"),
    path("post/<int:pk>/update/", views.PostUpdateView.as_view(), name="post-update"),
    path("post/<int:pk>/delete/", views.PostDeleteView.as_view(), name="post-delete"),
    path("post/<int:pk>/comments/new/", views.CommentCreateView.as_view(), name="create-comment"),
    path("comment/<int:pk>/update/", views.CommentUpdateView.as_view(), name="comment-edit"),
    path("comment/<int:pk>/delete/", views.CommentDeleteView.as_view(), name="comment-delete"),
    path("tags/<slug:tag_slug>/", views.PostByTagListView.as_view(), name="posts_by_tag"),
]
