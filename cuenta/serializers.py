from rest_framework import serializers
from .models import rubro, solicitud, horario

class rubroSerializer(serializers.ModelSerializer):
    class Meta:
        model = rubro
        fields = '__all__'
