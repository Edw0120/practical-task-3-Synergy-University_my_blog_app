from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('feed/', views.following_feed, name='following_feed'),
    path('<int:pk>/', views.post_detail, name='post_detail'),
    path('new/', views.post_new, name='post_new'),
    path('<int:pk>/edit/', views.post_edit, name='post_edit'),
    path('<int:pk>/delete/', views.post_delete, name='post_delete'),
    path('follow/<int:user_id>/', views.follow_user, name='follow_user'),
    path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow_user'),
    path('tag/<str:tag_name>/', views.posts_by_tag, name='posts_by_tag'),
    path('request-access/<int:post_pk>/', views.request_access, name='request_access'),
    path('manage-access/', views.manage_access_requests, name='manage_access_requests'),
    path('approve-request/<int:request_pk>/', views.approve_request, name='approve_request'),
    path('reject-request/<int:request_pk>/', views.reject_request, name='reject_request'),
]