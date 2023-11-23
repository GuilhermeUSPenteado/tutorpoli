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
from .models import Arquivo, Disciplina, Post, Comment, Profile, Reply
from .forms import CustomUserCreationForm, PostForm, CommentForm, ArquivoForm, DisciplinaForm, ReplyForm
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

from django.db.models import Q

def home(request):
    search_query = request.GET.get('search', '')
    if search_query:
        disciplinas = Disciplina.objects.filter(Q(name__icontains=search_query))
    else:
        disciplinas = Disciplina.objects.all()
    disciplinas_populares = Disciplina.objects.order_by('-contador')[:5]
    arquivos_populares = Arquivo.objects.order_by('-contador')[:3]
    disciplina_com_mais_posts = Disciplina.objects.annotate(num_posts=Count('post')).order_by('-num_posts')[:3]
    usuarios_ativos = Profile.objects.order_by('-tempo_ativo')[:5]
    usuarios_ativos = [
        {
            'username': profile.user.username,
            'horas_ativas': profile.tempo_ativo.total_seconds() // 3600
        }
        for profile in usuarios_ativos
    ]
    return render(request, 'home.html', {'disciplinas': disciplinas, 'disciplinas_populares': disciplinas_populares, 'arquivos_populares': arquivos_populares, 'disciplina_com_mais_posts': disciplina_com_mais_posts, 'usuarios_ativos': usuarios_ativos})

@login_required
def profile(request):
    if request.method == "POST":
        tipo = request.POST.get('tipo')
        biografia = request.POST.get('biografia')
        if tipo == 'T':
            return redirect('escolher_disciplinas')
        else:
            request.user.profile.tipo = 'A'
            if biografia is not None:
                request.user.profile.biografia = biografia
            request.user.profile.save()
            messages.success(request, 'Perfil atualizado com sucesso')
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
def escolher_disciplinas(request):
    if request.method == "POST":
        disciplinas_ids = request.POST.getlist('disciplinas')
        disciplinas = Disciplina.objects.filter(id__in=disciplinas_ids)
        request.user.profile.disciplinas.set(disciplinas)
        request.user.profile.tipo = 'T'
        request.user.profile.save()
        messages.success(request, 'Você agora é um Tutor')
        return redirect('profile')
    else:
        disciplinas = Disciplina.objects.all()
        return render(request, 'escolher_disciplinas.html', {'disciplinas': disciplinas})

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
    tempo_logado = datetime.now() - request.user.last_login
    profile = Profile.objects.get(user=request.user)
    profile.tempo_ativo += tempo_logado
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
    if request.user != post.author and request.user != post.disciplina.professor:
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

@login_required
def forum(request, disciplina_id):
    disciplina = get_object_or_404(Disciplina, pk=disciplina_id)
    posts = Post.objects.filter(disciplina=disciplina)
    return render(request, 'forum.html', {'disciplina': disciplina, 'posts': posts})

def disciplinas(request):
    disciplinas = Disciplina.objects.order_by('name')
    return render(request, 'disciplinas.html', {'disciplinas': disciplinas})

@login_required
def disciplina_detail(request, disciplina_id):
    disciplina = get_object_or_404(Disciplina, pk=disciplina_id)
    disciplina.contador += 1
    disciplina.save()
    if request.method == 'POST':
        return render(request, 'forum/disciplina_info.html', {'disciplina': disciplina})
    else:
        return render(request, 'forum/disciplina_detail.html', {'disciplina': disciplina})

@login_required
def disciplina_info(request, disciplina_id):
    disciplina = get_object_or_404(Disciplina, pk=disciplina_id)
    return render(request, 'forum/disciplina_info.html', {'disciplina': disciplina})

@login_required
def arquivos(request, disciplina_id):
    disciplina = get_object_or_404(Disciplina, pk=disciplina_id)
    return render(request, 'forum/arquivos.html', {'disciplina': disciplina})

@login_required
def provas(request, disciplina_id):
    disciplina = get_object_or_404(Disciplina, pk=disciplina_id)
    arquivos = Arquivo.objects.filter(disciplina=disciplina, tipo='P')
    for arquivo in arquivos:
        arquivo.contador += 1
        arquivo.save()
    if request.method == 'POST':
        form = ArquivoForm(request.POST, request.FILES)
        if form.is_valid():
            arquivo = form.save(commit=False)
            arquivo.disciplina = disciplina
            arquivo.tipo = 'P'
            arquivo.author = request.user
            arquivo.save()
            return redirect('provas', disciplina_id=disciplina.id)
    else:
        form = ArquivoForm()
    arquivos = Arquivo.objects.filter(disciplina=disciplina, tipo='P')
    return render(request, 'forum/provas.html', {'disciplina': disciplina, 'arquivos': arquivos, 'form': form})

@login_required
def resumos(request, disciplina_id):
    disciplina = get_object_or_404(Disciplina, pk=disciplina_id)
    arquivos = Arquivo.objects.filter(disciplina=disciplina, tipo='R')
    for arquivo in arquivos:
        arquivo.contador += 1
        arquivo.save()
    if request.method == 'POST':
        form = ArquivoForm(request.POST, request.FILES)
        if form.is_valid():
            arquivo = form.save(commit=False)
            arquivo.disciplina = disciplina
            arquivo.tipo = 'R'
            arquivo.author = request.user
            arquivo.save()
            return redirect('resumos', disciplina_id=disciplina.id)
    else:
        form = ArquivoForm()
    arquivos = Arquivo.objects.filter(disciplina=disciplina, tipo='R')
    return render(request, 'forum/resumos.html', {'disciplina': disciplina, 'arquivos': arquivos, 'form': form})

@login_required
def delete_arquivo(request, pk):
    arquivo = get_object_or_404(Arquivo, pk=pk)
    if request.user != arquivo.author:
        return HttpResponseForbidden('Você não tem permissão para excluir este arquivo.')
    if request.method == "POST":
        tipo = arquivo.tipo
        arquivo.delete()
        if tipo == 'R':
            return redirect('resumos', disciplina_id=arquivo.disciplina.id)
        else:
            return redirect('provas', disciplina_id=arquivo.disciplina.id)
    else:
        return render(request, 'forum/delete_arquivo.html', {'arquivo': arquivo})

@login_required
def disciplina_tutors(request, disciplina_id):
    disciplina = get_object_or_404(Disciplina, pk=disciplina_id)
    tutors = Profile.objects.filter(tipo='T', disciplinas=disciplina)
    if request.method == "POST":
        pass
    return render(request, 'forum/disciplina_tutors.html', {'disciplina': disciplina, 'tutors': tutors})

@login_required
def editar_disciplina(request, disciplina_id):
    disciplina = get_object_or_404(Disciplina, pk=disciplina_id)
    tutors = Profile.objects.filter(tipo='T', disciplinas=disciplina)
    if request.user.profile not in tutors and not request.user.is_superuser:
        return HttpResponseForbidden("Você não tem permissão para editar esta disciplina.")
    if request.method == "POST":
        form = DisciplinaForm(request.POST, instance=disciplina)
        if form.is_valid():
            form.save()
            messages.success(request, 'Informações da disciplina atualizadas com sucesso')
            return redirect('disciplina_info', disciplina_id=disciplina.id)
    else:
        form = DisciplinaForm(instance=disciplina)
    return render(request, 'forum/editar_disciplina.html', {'form': form, 'disciplina': disciplina})