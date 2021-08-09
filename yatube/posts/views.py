from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET
from yatube.settings import POSTS_ON_PAGE

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


@require_GET
def index(request):
    post_list = cache.get("index_page")
    if post_list is None:
        post_list = Post.objects.all()
        cache.set("index_page", post_list, timeout=20)
    paginator = Paginator(post_list, POSTS_ON_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    context = {
        "page": page,
    }
    return render(
        request, "posts/index.html", context
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group)
    paginator = Paginator(posts, POSTS_ON_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    context = {
        "group": group,
        "page": page,
    }
    return render(
        request, "posts/group.html", context
    )


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=author)
    paginator = Paginator(posts, POSTS_ON_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    posts_count = author.posts.count()
    following = False
    if request.user.is_authenticated:
        if Follow.objects.filter(
                user=request.user,
                author=author):
            following = True
        else:
            following = False
    context = {
        "user": request.user,
        "following": following,
        "author": author,
        "page": page,
        "posts": posts,
        "posts_count": posts_count,
        "paginator": paginator
    }
    return render(
        request, "posts/profile.html", context
    )


def post_view(request, username, post_id):
    author = User.objects.get(username=username)
    post = get_object_or_404(Post,
                             author=author,
                             pk=post_id)
    posts_count = author.posts.count()
    form = CommentForm()
    comments = post.comments.all()
    context = {
        "author": author,
        "post": post,
        "posts_count": posts_count,
        "form": form,
        "comments": comments
    }
    if request.method == "POST":
        comment_form = CommentForm(data=request.POST or None)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect("post", username, post_id)
    return render(
        request, "posts/post.html", context
    )


@login_required
def new_post(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("index")
    form = PostForm()
    return render(
        request, "posts/new_post.html", {"form": form}
    )


@login_required
def post_edit(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=profile)
    if request.user != profile:
        return redirect('post', username=username, post_id=post_id)

    form = PostForm(request.POST or None,
                    files=request.FILES or None, instance=post)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect("post", username=request.user.username,
                            post_id=post_id)

    return render(
        request, 'posts/post_edit.html', {'form': form, 'post': post},
    )


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username,
                             pk=post_id)
    comment_form = CommentForm(request.POST or None)
    if comment_form.is_valid():
        comment = comment_form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect("post", username, post_id)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user.is_authenticated:
        if request.user != author:
            Follow.objects.get_or_create(author=author,
                                         user=request.user)
        return redirect("profile", username)
    return redirect("auth/login/")


@login_required
def profile_unfollow(request, username):
    Follow.objects.filter(
        author__username=username,
        user=request.user).delete()
    return redirect("profile", username)


@login_required
def follow_index(request):
    follows = Follow.objects.filter(
        user=request.user
    )
    authors = [follow.author
               for follow in follows]
    posts = Post.objects.filter(
        author__in=authors
    )
    paginator = Paginator(posts, POSTS_ON_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    template = "posts/follow.html"
    return render(
        request,
        template,
        {
            "posts": posts,
            "paginator": paginator,
            "page": page,
        }
    )
