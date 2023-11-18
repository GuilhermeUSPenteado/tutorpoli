from django.db import models

class Disciplina(models.Model):
    name = models.CharField(max_length=200)
    horario_monitoria = models.TextField()
    dia_da_semana = models.TextField()
    sala = models.TextField()
    nome_monitor = models.TextField()
    
    def __str__(self):
        return self.name