from asyncio import AbstractServer
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from tutorpoli.settings import TIME_ZONE

class Disciplina(models.Model):
    name = models.CharField(max_length=200)
    horario_monitoria = models.TextField()
    dia_da_semana = models.TextField()
    sala = models.TextField()
    nome_monitor = models.TextField()
    def __str__(self):
        return self.name
    
class Profile(models.Model):
    TIPOS = (
        ('A', 'Aluno'),
        ('T', 'Tutor'),
        ('AD', 'Administrador'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=2, choices=TIPOS, default='A')
    disciplinas = models.ManyToManyField(Disciplina, blank=True)
    biografia = models.TextField(blank=True)

class Post(models.Model):
    title = models.CharField("Título", max_length=200)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    content = models.TextField("Conteúdo")
    post_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    def publish(self):
        self.published_date = timezone.now()
        self.save()
    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey('forum.Post', on_delete=models.CASCADE, related_name='comments')
    disciplina = models.ForeignKey('forum.Disciplina', on_delete=models.CASCADE, related_name='comments', null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField("Conteúdo")
    created_date = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_date']
    def __str__(self):
        return self.text
    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'pk': self.post.pk})

class Reply(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField("Conteúdo")
    created_date = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_date']
    def __str__(self):
        return self.text
    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'pk': self.comment.post.pk})