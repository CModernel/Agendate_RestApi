from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(rubro)
admin.site.register(empresa)
admin.site.register(usuariosEmpresa)
admin.site.register(horario)
admin.site.register(solicitud)
