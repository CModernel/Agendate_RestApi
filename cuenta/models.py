from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from .utils import rango_horas, intervalo_horas
# Create your models here.
    
class rubro(models.Model):
    rubroNom = models.CharField(max_length=20,null=True)

    def __str__(self):
        return self.rubroNom
        
# esta clase ordena los Rubros alfabéticamente
    class Meta:
        ordering = ["rubroNom"]

class empresa(models.Model):
    EmpId = models.AutoField(primary_key=True)
    EmpRUT = models.CharField(max_length=12,null=True, blank=True)
    EmpRazonSocial = models.CharField(max_length=50,null=True)
    EmpDirCalle = models.CharField(max_length=50, null=True)
    EmpDirEsquina = models.CharField(max_length=30, null=True, blank=True)
    EmpDirNum = models.CharField(max_length=30, null=True, blank=True)
    EmpDirEmail = models.EmailField(null=True)
    EmpTelefono = models.CharField(max_length=12, null=True, blank=True)
    EmpDescripcion = models.TextField(null=True, blank=True)
    EmpRubro1 = models.ForeignKey(rubro, null=True, blank=True, on_delete=models.SET_NULL, related_name='EmpRubro1')
    EmpRubro2 = models.ForeignKey(rubro, null=True, blank=True, on_delete=models.SET_NULL, related_name='EmpRubro2')
    EmpActivo = models.BooleanField(null=False, default=True)
    EmpImagen = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.EmpRazonSocial

class usuariosEmpresa(models.Model):
    ROLES = (
        ('Admin','Admin'),
        ('Sub-Admin','Sub-Admin'),
        )
        
    UsuId = models.ForeignKey(User, on_delete=models.CASCADE)
    EmpId = models.ForeignKey(empresa, on_delete=models.CASCADE)
    UsuEmpRol = models.CharField(max_length=15, null=False, choices=ROLES)
    UsuEmpActivo = models.BooleanField(null=False, default=True)

    class Meta:
        unique_together = (('UsuId', 'EmpId'))
    
    def __str__(self):
        return str(self.EmpId)

# Devuelve True si es admin o sub-admin (tabla UsuariosEmpresa)
# Nos sirve para imprimir Barra Navegacion si es Admin o Sub-Admin
def es_admin(user):
    usuEmp = usuariosEmpresa.objects.filter(UsuId=user.id, UsuEmpActivo=True)
    if usuEmp.count() > 0:
        return True
    
    return False

class horario(models.Model):
    intervalos_horas = intervalo_horas()
    EmpId = models.OneToOneField(empresa, primary_key=True, on_delete=models.CASCADE)
    LunesDesde = models.TimeField(auto_now=False, auto_now_add=False, null=True, blank=True, choices=intervalos_horas)
    LunesHasta = models.TimeField(auto_now=False, auto_now_add=False, null=True, blank=True, choices=intervalos_horas)
    MartesDesde = models.TimeField(auto_now=False, auto_now_add=False, null=True, blank=True, choices=intervalos_horas)
    MartesHasta = models.TimeField(auto_now=False, auto_now_add=False, null=True, blank=True, choices=intervalos_horas)
    MiercolesDesde = models.TimeField(auto_now=False, auto_now_add=False, null=True, blank=True, choices=intervalos_horas)
    MiercolesHasta = models.TimeField(auto_now=False, auto_now_add=False, null=True, blank=True, choices=intervalos_horas)
    JuevesDesde = models.TimeField(auto_now=False, auto_now_add=False, null=True, blank=True, choices=intervalos_horas)
    JuevesHasta = models.TimeField(auto_now=False, auto_now_add=False, null=True, blank=True, choices=intervalos_horas)
    ViernesDesde = models.TimeField(auto_now=False, auto_now_add=False, null=True, blank=True, choices=intervalos_horas)
    ViernesHasta = models.TimeField(auto_now=False, auto_now_add=False, null=True, blank=True, choices=intervalos_horas)
    SabadoDesde = models.TimeField(auto_now=False, auto_now_add=False, null=True, blank=True, choices=intervalos_horas)
    SabadoHasta = models.TimeField(auto_now=False, auto_now_add=False, null=True, blank=True, choices=intervalos_horas)
    DomingoDesde = models.TimeField(auto_now=False, auto_now_add=False, null=True, blank=True, choices=intervalos_horas)
    DomingoHasta = models.TimeField(auto_now=False, auto_now_add=False, null=True, blank=True, choices=intervalos_horas)

    def __str__(self):
        return str(self.EmpId)


class solicitud(models.Model):
    UsuId = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    EmpId = models.ForeignKey(empresa, on_delete=models.DO_NOTHING)
    UsuAdminResponsable = models.ForeignKey(usuariosEmpresa, on_delete=models.DO_NOTHING, related_name='UsuAdminResponsable')
    FechaSolicitud = models.DateField(auto_now=False, auto_now_add=False)
    HoraSolicitud = models.TimeField(auto_now=False, auto_now_add=False)
    SeConcreto = models.BooleanField(null=False,default=False)
    ComentarioAdmin = models.CharField(max_length=200, null=True, blank=True)
    ComentarioUsuario = models.CharField(max_length=200, null=True, blank=True)
    SolicitudActivo = models.BooleanField(null=False, blank=False, default=True)

    def __str__(self):
        return str(self.UsuId)
    
# esta clase ordena los Items cronológicamente
    class Meta:
        ordering = ["UsuId" , "FechaSolicitud", "HoraSolicitud"]