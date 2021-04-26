from rest_framework import serializers
from .models import rubro, empresa, solicitud, horario
from django.contrib.auth.models import User

class rubroSerializer(serializers.ModelSerializer):
    class Meta:
        model = rubro
        fields = '__all__'

class elegirServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = empresa
        fields = '__all__'

class verAgendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = solicitud
        fields = '__all__'

class verMiPerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']