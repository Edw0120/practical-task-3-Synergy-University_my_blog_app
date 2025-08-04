from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404, HttpResponseForbidden
from django.contrib.auth.models import User
from .models import Post, Follow, Tag, Comment, AccessRequest
from .forms import PostForm, CommentForm
from django.db.models import Q
from django.utils import timezone


def post_list(request):
    posts = Post.objects.filter(status='public').order_by('-created_at')
    context = {
        'posts': posts
    }
    return render(request, 'posts/post_list.html', context)


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.all()

    is_following = False
    if request.user.is_authenticated and request.user != post.author:
        is_following = Follow.objects.filter(follower=request.user, following=post.author).exists()

    can_view_hidden_post = False
    access_request_status = None
    if post.status == 'hidden_request':
        if request.user.is_authenticated:
            if request.user == post.author:
                can_view_hidden_post = True
            else:
                existing_request = AccessRequest.objects.filter(post=post, requester=request.user).first()
                if existing_request:
                    access_request_status = existing_request.status
                    if existing_request.status == 'approved':
                        can_view_hidden_post = True
        
        if not can_view_hidden_post:
            context = {
                'post': post,
                'access_request_status': access_request_status,
                'is_following': is_following,
            }
            return render(request, 'posts/post_hidden_request_teaser.html', context)

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Для комментирования необходимо войти.")
            return redirect('login')
        
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.author = request.user
            new_comment.save()
            messages.success(request, "Ваш комментарий добавлен!")
            return redirect('posts:post_detail', pk=post.pk)
        else:
            messages.error(request, "Ошибка при добавлении комментария. Пожалуйста, исправьте ошибки.")
    else:
        comment_form = CommentForm()

    context = {
        'post': post,
        'is_following': is_following,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            # form.save_m2m() # УДАЛИТЬ ЭТУ СТРОКУ
            messages.success(request, "Ваш пост успешно опубликован!")
            return redirect('posts:post_detail', pk=post.pk)
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = PostForm()
    return render(request, 'posts/post_edit.html', {'form': form, 'page_title': 'Написать новый пост'})


@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.user != post.author:
        messages.error(request, "У вас нет прав для редактирования этого поста.")
        return redirect('posts:post_detail', pk=post.pk)

    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            # form.save_m2m() # УДАЛИТЬ ЭТУ СТРОКУ
            messages.success(request, "Пост успешно обновлен!")
            return redirect('posts:post_detail', pk=post.pk)
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = PostForm(instance=post)
    return render(request, 'posts/post_edit.html', {'form': form, 'page_title': 'Редактировать пост'})


@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.user != post.author:
        messages.error(request, "У вас нет прав для удаления этого поста.")
        return redirect('posts:post_detail', pk=post.pk)

    if request.method == "POST":
        post.delete()
        messages.success(request, "Пост успешно удален!")
        return redirect('posts:post_list')
    return render(request, 'posts/post_confirm_delete.html', {'post': post})


@login_required
def follow_user(request, user_id):
    user_to_follow = get_object_or_404(User, pk=user_id)
    if request.user == user_to_follow:
        messages.error(request, "Вы не можете подписаться на себя.")
        return redirect(request.META.get('HTTP_REFERER', 'posts:post_list'))

    if not Follow.objects.filter(follower=request.user, following=user_to_follow).exists():
        Follow.objects.create(follower=request.user, following=user_to_follow)
        messages.success(request, f"Вы успешно подписались на {user_to_follow.username}.")
    else:
        messages.info(request, f"Вы уже подписаны на {user_to_follow.username}.")
    return redirect(request.META.get('HTTP_REFERER', 'posts:post_list'))


@login_required
def unfollow_user(request, user_id):
    user_to_unfollow = get_object_or_404(User, pk=user_id)
    if request.user == user_to_unfollow:
        messages.error(request, "Вы не можете отписаться от себя.")
        return redirect(request.META.get('HTTP_REFERER', 'posts:post_list'))

    follow_instance = Follow.objects.filter(follower=request.user, following=user_to_unfollow)
    if follow_instance.exists():
        follow_instance.delete()
        messages.success(request, f"Вы успешно отписались от {user_to_unfollow.username}.")
    else:
        messages.info(request, f"Вы не подписаны на {user_to_unfollow.username}.")
    return redirect(request.META.get('HTTP_REFERER', 'posts:post_list'))


@login_required
def following_feed(request):
    followed_users_ids = request.user.following_set.values_list('following__id', flat=True)

    posts = Post.objects.filter(
        Q(author__in=followed_users_ids) & Q(status='public')
    ).order_by('-created_at')

    context = {
        'posts': posts,
        'feed_title': 'Лента подписок'
    }
    return render(request, 'posts/post_list.html', context)


def posts_by_tag(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)
    posts = Post.objects.filter(tags=tag, status='public').order_by('-created_at')
    context = {
        'posts': posts,
        'feed_title': f'Посты по тегу: #{tag_name}'
    }
    return render(request, 'posts/post_list.html', context)


@login_required
def request_access(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk)

    if post.status != 'hidden_request':
        messages.error(request, "Этот пост не требует запроса доступа.")
        return redirect('posts:post_detail', pk=post.pk)

    if request.user == post.author:
        messages.info(request, "Вы являетесь автором этого поста.")
        return redirect('posts:post_detail', pk=post.pk)

    existing_request = AccessRequest.objects.filter(post=post, requester=request.user).first()
    if existing_request:
        if existing_request.status == 'pending':
            messages.info(request, "Вы уже отправили запрос на доступ к этому посту. Ожидается рассмотрение.")
        elif existing_request.status == 'approved':
            messages.success(request, "Вам уже предоставлен доступ к этому посту.")
        elif existing_request.status == 'rejected':
            messages.warning(request, "Ваш предыдущий запрос на доступ был отклонен.")
        return redirect('posts:post_detail', pk=post.pk)

    AccessRequest.objects.create(post=post, requester=request.user, status='pending')
    messages.success(request, "Запрос на доступ успешно отправлен автору поста!")
    return redirect('posts:post_detail', pk=post.pk)


@login_required
def manage_access_requests(request):
    pending_requests = AccessRequest.objects.filter(
        post__author=request.user,
        status='pending'
    ).order_by('-requested_at')

    context = {
        'pending_requests': pending_requests,
        'page_title': 'Управление запросами на доступ к моим постам'
    }
    return render(request, 'posts/manage_access_requests.html', context)


@login_required
def approve_request(request, request_pk):
    access_request = get_object_or_404(AccessRequest, pk=request_pk)

    if request.user != access_request.post.author:
        messages.error(request, "У вас нет прав для управления этим запросом.")
        return redirect('posts:manage_access_requests')

    if request.method == 'POST':
        access_request.status = 'approved'
        access_request.response_at = timezone.now()
        access_request.save()
        messages.success(request, f"Запрос от {access_request.requester.username} одобрен.")
    return redirect('posts:manage_access_requests')


@login_required
def reject_request(request, request_pk):
    access_request = get_object_or_404(AccessRequest, pk=request_pk)

    if request.user != access_request.post.author:
        messages.error(request, "У вас нет прав для управления этим запросом.")
        return redirect('posts:manage_access_requests')

    if request.method == 'POST':
        access_request.status = 'rejected'
        access_request.response_at = timezone.now()
        access_request.save()
        messages.warning(request, f"Запрос от {access_request.requester.username} отклонен.")
    return redirect('posts:manage_access_requests')