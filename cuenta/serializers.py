from rest_framework import serializers
from .models import rubro, empresa, solicitud, horario

class rubroSerializer(serializers.ModelSerializer):
    class Meta:
        model = rubro
        fields = '__all__'

#        'verAgendaV1':'/verAgendaV1/',
#        'seleccionarRubroV1':'/seleccionarRubroV1/',
#        'elegirServicioV1':'/elegirServicioV1/<str:rubro>/',
#        'elegirHorarioV1':'/elegirHorarioV1/<str:empresaSel>/<str:fechaSel>',

class elegirServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = empresa
        fields = '__all__'