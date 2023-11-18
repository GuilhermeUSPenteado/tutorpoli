from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings

urlpatterns = [
    path('', views.home, name='home'),
    path('disciplina/<int:disciplina_id>/', views.disciplina_detail, name='disciplina_detail'),
]