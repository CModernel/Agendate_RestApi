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

    path('ajax/obtenerUsuario/', ajax.obtenerUsuario, name="obtenerUsuario"),

    path('api/', views.apiList, name="apiList"),
    path('api/getAllRubrosV1/', views.getAllRubrosV1, name="getAllRubrosV1"),
    path('api/getAllEmpresasV1/', views.getAllEmpresasV1, name="getAllEmpresasV1"),
    path('api/elegirServicioV1/<str:rubro>/', views.elegirServicioV1, name="elegirServicioV1"),
    path('api/elegirHorarioV1/<str:empresaSel>/<str:fechaSel>/', views.getHorarioSolicitudEmpresaPorFechaV1, name="getHorarioSolicitudEmpresaPorFechaV1"),
]
