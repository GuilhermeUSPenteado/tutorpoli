from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.urls import reverse_lazy
from django.views import generic
from django import forms
from .models import Disciplina
from .forms import DisciplinaForm

def home(request):
    return render(request, 'home.html')

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
