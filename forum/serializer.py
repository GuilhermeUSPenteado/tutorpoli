from rest_framework import serializers
from .models import Disciplina

class DataSerializer(serializers.ModelSerializer):
    class Meta:
        model=Disciplina
        fields=('name','horario_monitoria','dia_da_semana','sala','nome_monitor','contador')