from django.urls import path
from django.conf.urls import url
from . import views, ajax
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('registro/', views.registro, name="registro"),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUsuario, name="logout"),

    path('', views.home, name="home"),
    path('agendar/', views.agendar, name="agendar"),
    path('verAgenda/', views.verAgenda),
    path('elegirServicio/<str:rubro>/', views.elegirServicio, name="servicio"),
    path('elegirHorario/<str:empresaSel>/<str:fechaSel>', views.elegirHorario, name="horario"),
    path('aceptarSolicitud/<str:empresaSel>/<str:fecha>/<str:hora>', views.aceptarSolicitud, name="solicitud"),
    path('modificarDatos/', views.modificarDatos, name="modificarDatos"),
    path('bajaSolicitud/<str:solicitudSel>', views.bajaSolicitud, name="bajaSolicitud"),
    path('bajaSistema/', views.bajaSistema),
    path('quienesSomos/', views.quienesSomos),
    path('mision/', views.mision),
    path('contacto/', views.contacto),

    path('administrador/', views.administrador, name="administrador"),
    path('seleccionEmpresa/', views.seleccionEmpresa, name="seleccionEmpresa"),
    path('crearEmpresa/', views.crearEmpresa, name="crearEmpresa"),
    path('verAgendaEmpresa/', views.verAgendaEmpresa, name="verAgendaEmpresa"),
    path('administrarEmpresa/altaEmpleado/', views.altaEmpleado, name="altaEmpleado"),
    path('administrarEmpresa/bajaEmpleado/', views.bajaEmpleado, name="bajaEmpleado"),
    path('administrarEmpresa/bajaEmpleadoConfirmar/<str:UsuId>', views.bajaEmpleadoConfirmar, name="bajaEmpleadoConfirmar"),
    path('administrarEmpresa/modificarEmpresa/', views.modificarEmpresa, name="modificarEmpresa"),
    path('administrarEmpresa/modificarHorarios/', views.modificarHorarios, name="modificarHorarios"),

    
    path('administrarEmpresa/bajaEmpresa', views.bajaEmpresa, name="bajaEmpresa"),

    path('ajax/obtenerUsuario/', ajax.obtenerUsuario, name="obtenerUsuario")
]
