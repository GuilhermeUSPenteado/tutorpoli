from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings

urlpatterns = [
    path('', views.home, name='home'),
    path('posts/<int:disciplina_id>/', views.post_list, name='post_list'),
    path('users/', views.user_list, name='user_list'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/new/<int:disciplina_id>/', views.post_new, name='post_new'),
    path('post/<int:pk>/edit/<int:disciplina_id>/', views.post_edit, name='post_edit'),
    path('post/<int:pk>/delete/<int:disciplina_id>/', views.post_delete, name='post_delete'),
    path('post/<int:pk>/comment/<int:disciplina_id>/', views.add_comment_to_post, name='add_comment_to_post'),
    path('comment/<int:pk>/edit/<int:disciplina_id>/', views.edit_comment, name='edit_comment'),
    path('comment/<int:pk>/delete/<int:disciplina_id>/', views.delete_comment, name='delete_comment'),
    path('comment/<int:pk>/reply/<int:disciplina_id>/', views.add_reply_to_comment, name='add_reply_to_comment'),
    path('reply/<int:pk>/edit/<int:disciplina_id>/', views.edit_reply, name='edit_reply'),
    path('reply/<int:pk>/delete/<int:disciplina_id>/', views.delete_reply, name='delete_reply'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('accounts/profile/', views.profile, name='profile'),
    path('users/', views.user_list, name='user_list'),
    path('users/<int:user_id>/', views.user_profile, name='user_profile'),
    path('disciplina/<int:disciplina_id>/', views.disciplina_detail, name='disciplina_detail'),
    path('disciplina/<int:disciplina_id>/arquivos/', views.arquivos, name='arquivos'),
    path('edit_biography/', views.edit_biography, name='edit_biography'),
]