from django.contrib import admin
from .models import Disciplina, Post, Comment, Reply

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Disciplina)
admin.site.register(Reply)