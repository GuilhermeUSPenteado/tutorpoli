from django import forms
from .models import Disciplina
   
class DisciplinaForm(forms.ModelForm):
    class Meta:
        model = Disciplina
        fields = ['horario_monitoria', 'dia_da_semana', 'sala', 'nome_monitor']