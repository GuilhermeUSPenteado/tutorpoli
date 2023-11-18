from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponseForbidden, FileResponse, Http404
from django.db.models import Q, Count, F
from django.urls import reverse_lazy
from django.views import generic
from django import forms
from .models import Disciplina, Post, Comment, Profile, Reply
from .forms import CustomUserCreationForm, PostForm, CommentForm, DisciplinaForm, ReplyForm
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.is_superuser:
            Profile.objects.create(user=instance, tipo='AD')
        else:
            Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

def home(request):
    disciplinas = Disciplina.objects.all()
    return render(request, 'home.html', {'disciplinas': disciplinas})

@login_required
def profile(request):
    if request.method == "POST":
        tipo = request.POST.get('tipo')
        biografia = request.POST.get('biografia')
    return render(request, 'profile.html')

@login_required
def edit_biography(request):
    if request.method == "POST":
        biografia = request.POST['biografia']
        request.user.profile.biografia = biografia
        request.user.profile.save()
        messages.success(request, 'Biografia atualizada com sucesso')
        return redirect('profile')
    return render(request, 'edit_biography.html')

@login_required
def user_list(request):
    users = User.objects.all()
    return render(request, 'forum/user_list.html', {'users': users})

@login_required
def user_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.user.is_authenticated and request.user.id == user_id:
        return redirect('profile')
    return render(request, 'user_profile.html', {'user': user})

class SignUpView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

def logout_view(request):
    profile = Profile.objects.get(user=request.user)
    profile.save()
    logout(request)
    return redirect('base')

@login_required
def post_list(request, disciplina_id):
    search_query = request.GET.get('search', '')
    disciplina = get_object_or_404(Disciplina, pk=disciplina_id)
    posts = Post.objects.filter(Q(title__icontains=search_query), disciplina_id=disciplina_id).order_by('-post_date')
    num_posts = posts.count()
    return render(request, 'forum/post_list.html', {'posts': posts, 'disciplina': disciplina, 'num_posts': num_posts})

@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = Comment.objects.filter(post=post)
    return render(request, 'forum/post_detail.html', {'post': post, 'comments': comments})

@login_required
def post_new(request, disciplina_id):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            form.save_m2m()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(initial={'disciplina': disciplina_id})
    return render(request, 'forum/post_edit.html', {'form': form})

@login_required
def post_edit(request, pk, disciplina_id):
    post = get_object_or_404(Post, pk=pk)
    if request.user != post.author and request.user != post.disciplina.professor:
        return HttpResponseForbidden()
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            form.save_m2m()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'forum/post_edit.html', {'form': form})

@login_required
def post_delete(request, pk, disciplina_id):
    post = get_object_or_404(Post, pk=pk)
    if request.user != post.author:
        return HttpResponseForbidden()
    if request.method == "POST":
        post.delete()
        return redirect('post_list', disciplina_id=disciplina_id)
    else:
        return render(request, 'forum/post_confirm_delete.html', {'post': post})

@login_required
def add_comment_to_post(request, pk, disciplina_id):
    post = get_object_or_404(Post, pk=pk)
    disciplina = get_object_or_404(Disciplina, pk=disciplina_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.disciplina = disciplina
            comment.author = request.user
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm(initial={'disciplina': disciplina})
    comments = Comment.objects.filter(post=post)
    return render(request, 'forum/add_comment_to_post.html', {'form': form, 'comments': comments})

@login_required
def edit_comment(request, pk, disciplina_id):
    comment = get_object_or_404(Comment, pk=pk)
    disciplina = get_object_or_404(Disciplina, pk=disciplina_id)
    if request.user != comment.author:
        return HttpResponseForbidden('Você não tem permissão para editar este comentário.')
    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            comment = form.save()
            return redirect('post_detail', pk=comment.post.pk)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'forum/edit_comment.html', {'form': form})

@login_required
def delete_comment(request, pk, disciplina_id):
    comment = get_object_or_404(Comment, pk=pk)
    disciplina = get_object_or_404(Disciplina, pk=disciplina_id)
    if request.user != comment.author:
        return HttpResponseForbidden('Você não tem permissão para excluir este comentário.')
    if request.method == "POST":
        comment.delete()
        return redirect('post_detail', pk=comment.post.pk)
    else:
        return render(request, 'forum/delete_comment.html', {'comment': comment})

@login_required
def add_reply_to_comment(request, pk, disciplina_id):
    comment = get_object_or_404(Comment, pk=pk)
    if request.method == "POST":
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.comment = comment
            reply.author = request.user
            reply.save()
            return redirect('post_detail', pk=comment.post.pk)
    else:
        form = ReplyForm()
    return render(request, 'forum/add_reply_to_comment.html', {'form': form})

@login_required
def edit_reply(request, pk, disciplina_id):
    reply = get_object_or_404(Reply, pk=pk)
    if request.user != reply.author:
        return HttpResponseForbidden('Você não tem permissão para editar esta resposta.')
    if request.method == "POST":
        form = ReplyForm(request.POST, instance=reply)
        if form.is_valid():
            reply = form.save()
            return redirect('post_detail', pk=reply.comment.post.pk)
    else:
        form = ReplyForm(instance=reply)
    return render(request, 'forum/edit_reply.html', {'form': form})

@login_required
def delete_reply(request, pk, disciplina_id):
    reply = get_object_or_404(Reply, pk=pk)
    if request.user != reply.author:
        return HttpResponseForbidden('Você não tem permissão para excluir esta resposta.')
    if request.method == "POST":
        reply.delete()
        return redirect('post_detail', pk=reply.comment.post.pk)
    else:
        return render(request, 'forum/delete_reply.html', {'reply': reply})

def forum(request, disciplina_id):
    disciplina = get_object_or_404(Disciplina, pk=disciplina_id)
    return render(request, 'forum.html', {'disciplina': disciplina})

def disciplinas(request):
    disciplinas = Disciplina.objects.order_by('name')
    return render(request, 'disciplinas.html', {'disciplinas': disciplinas})

def disciplina_detail(request, disciplina_id):
    disciplina = get_object_or_404(Disciplina, pk=disciplina_id)
    if request.method == 'POST':
        return render(request, 'forum/disciplina_detail.html', {'disciplina': disciplina})
