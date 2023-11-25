from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Disciplina, Post, Comment, Arquivo, Reply

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Obrigatório.', label='Nome')
    last_name = forms.CharField(max_length=30, required=True, help_text='Obrigatório.', label='Sobrenome')
    email = forms.EmailField(max_length=254, help_text='Obrigatório. Informe um email válido.')
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )

class ArquivoForm(forms.ModelForm):
    class Meta:
        model = Arquivo
        fields = ['titulo', 'arquivo',]

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'content', 'disciplina')
        widgets = {
            'disciplina': forms.HiddenInput()
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
    def clean_text(self):
        text = self.cleaned_data.get('text')
        if not text:
            raise forms.ValidationError('O campo de texto é obrigatório.')
        if len(text) > 500:
            raise forms.ValidationError('O texto não pode ter mais de 500 caracteres.')
        return text

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ('text',)
    def clean_text(self):
        text = self.cleaned_data.get('text')
        if not text:
            raise forms.ValidationError('O campo de texto é obrigatório.')
        if len(text) > 500:
            raise forms.ValidationError('O texto não pode ter mais de 500 caracteres.')
        return text
    
class DisciplinaForm(forms.ModelForm):
    class Meta:
        model = Disciplina
        fields = ['horario_monitoria', 'dia_da_semana', 'sala', 'nome_monitor']

class RegisterForm(UserCreationForm):
    email = forms.EmailField(max_length=254)

    class Meta:
        model = User
        fields = ('username',  'email', 'password1', 'password2', )