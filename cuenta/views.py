from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.messages import constants
from django.http import JsonResponse

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import serializers
import json

from cuenta.forms import FormularioCreacionUsuario, FormularioModificarUsuario, FormularioElegirHorario, FormularioEmpresa, FormularioHorarios
from cuenta.models import solicitud, empresa, rubro, horario, User, usuariosEmpresa
from cuenta.utils import rango_horas, es_numerico
import datetime
from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from .decorators import usuario_noAutenticado,  solo_admin, solo_admin_empresa, solo_admin_grupo, solo_usuario, validacion_cant_empresas

#para los mails
from django.core.mail import send_mail, EmailMessage
from django.conf import settings

#Serializador
from .models import rubro
from .serializers import rubroSerializer, elegirServicioSerializer

@usuario_noAutenticado
def registro(request):
    form = FormularioCreacionUsuario()
    if request.method == 'POST':
        form = FormularioCreacionUsuario(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, 'La cuenta '+ user +' fue creada exitosamente.')
            
            return redirect('login')

    context = {'form':form}
    return render(request, 'cuenta/registro.html', context)


def empresaMultiple(request):
    return (usuariosEmpresa.objects.filter(UsuId=request.user.id, UsuEmpActivo=True).count() > 1)


# Devuelve primera empresa disponible
def empresaPorDefecto(request):
    return usuariosEmpresa.objects.filter(UsuId=request.user.id, UsuEmpActivo=True).first()


@usuario_noAutenticado
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            empresaSel = empresaPorDefecto(request)
            if(empresaSel is not None):
                request.session['empresaSel'] = empresaSel.EmpId_id
                request.session['empresaSelNombre'] = empresaSel.EmpId.EmpRazonSocial
                request.session['empresaMultiple'] = empresaMultiple(request)
                request.session['empresaSelRol'] = empresaSel.UsuEmpRol

            return redirect('seleccionEmpresa')
        else:
            messages.info(request, 'Usuario y/o Contraseña incorrecta')

    context = {}
    return render(request, 'cuenta/login.html', context)


def logoutUsuario(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
@solo_usuario
def home(request):
    solicitudes = solicitud.objects.filter(UsuId=request.user, FechaSolicitud=datetime.date.today(), SolicitudActivo=True)
    rubros = rubro.objects.all()
    hoy = datetime.date.today()
    return render(request, 'cuenta/tablero.html', {'rubros': rubros, 'solicitudes':solicitudes, 'fecha': hoy})


@login_required(login_url='login')
def agendar(request):
    solicitudes = solicitud.objects.filter(UsuId=request.user, FechaSolicitud=datetime.date.today(), SolicitudActivo=True)
    rubros = rubro.objects.all()
    hoy = datetime.date.today()
    return render(request, 'cuenta/tablero.html', {'rubros': rubros, 'solicitudes':solicitudes, 'fecha': hoy})


@login_required(login_url='login')
@solo_admin
def administrador(request):
    solicitudes = {}
    if 'empresaSel' in request.session:
        if (request.session['empresaSel'] is not None):
            solicitudes = solicitud.objects.filter(EmpId=request.session['empresaSel'], FechaSolicitud=datetime.date.today(), SolicitudActivo=True)
    hoy = datetime.date.today()
    return render(request, 'cuenta/tableroAdmin.html', {'solicitudes':solicitudes, 'fecha': hoy})


@login_required(login_url='login')
def verAgenda(request):
    solicitudes = solicitud.objects.filter(UsuId=request.user, FechaSolicitud__gte=datetime.date.today(), SolicitudActivo=True)
    return render(request, 'cuenta/verAgenda.html', {'solicitudes': solicitudes})


@login_required(login_url='login')
def elegirServicio(request, rubro):
    servicios = (empresa.objects.filter(EmpRubro1=rubro) & empresa.objects.filter(EmpActivo=True)) | (empresa.objects.filter(EmpRubro2=rubro) & empresa.objects.filter(EmpActivo=True))
    context = {'servicios': servicios}
    return render(request, 'cuenta/elegirServicio.html', context)


@login_required(login_url='login')
def elegirHorario(request, empresaSel, fechaSel):
    empresaSeleccion = empresa.objects.filter(EmpId=empresaSel, EmpActivo=True).first()
    horarioEmpresa = horario.objects.filter(EmpId=empresaSel).first()
    solicitudesSet = set(solicitud.objects.filter(FechaSolicitud=fechaSel, EmpId=empresaSel, SolicitudActivo=True).values_list('HoraSolicitud', flat=True))

    solicitudes = set()
    for i in solicitudesSet:
        solicitudes.add(i.strftime("%H:%M"))
        
    desdeHasta = ["Desde", "Hasta"]
    dias = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes","Sabado","Domingo"]
    fecha = datetime.datetime.strptime(fechaSel, "%Y-%m-%d").date()
    numDia = fecha.weekday()

    horarioDesde = getattr(horarioEmpresa, dias[numDia]+desdeHasta[0])
    horarioHasta = getattr(horarioEmpresa, dias[numDia]+desdeHasta[1])

    context = {}
    listaHorarios = []
    listaHorariosVencidos = []
    if horarioDesde is None or horarioHasta is None:
        messages.error(request, 'La empresa "' + empresaSeleccion.EmpRazonSocial + '" se encuentra cerrada los dias ' + dias[numDia], extra_tags='alert alert-warning')
    else:
        inicio = datetime.datetime.now().replace(hour=horarioDesde.hour, minute=horarioDesde.minute, second=horarioDesde.second)
        fin = datetime.datetime.now().replace(hour=horarioHasta.hour, minute=horarioHasta.minute, second=horarioHasta.second)
        listaHorarios = [ dt.strftime('%H:%M') for dt in rango_horas(inicio, fin, timedelta(minutes=30)) ]

# para filtrar que muestre: desde ahora(+59 min) en adelante pasando por parámetro una lista de horarios vencidos
# ojo * fechaSer viene en formato str   
        if fechaSel == str(date.today()) :
            fin = datetime.datetime.now() + timedelta(minutes=59)
            listaHorariosVencidos = [ dt.strftime('%H:%M') for dt in rango_horas(inicio, fin, timedelta(minutes=30)) ]

    context = {'empresa': empresaSeleccion, 'listaHorarios': listaHorarios, 'solicitudes': solicitudes, 'fechaSel': fechaSel, "listaHorariosVencidos":listaHorariosVencidos}
    
    return render(request, 'cuenta/elegirHorario.html', context)

@login_required(login_url='login')
def aceptarSolicitud(request, empresaSel, fecha, hora):
    empresaSeleccion = empresa.objects.filter(EmpId=empresaSel).first()
    context = {'empresaSel': empresaSeleccion, 'fecha': fecha, 'hora': hora}
    if request.method == 'POST':
        usuAdmin = usuariosEmpresa.objects.filter(EmpId_id=empresaSel, UsuEmpRol='Admin').first()
        if(usuAdmin is None):
            usuAdmin = usuariosEmpresa.objects.filter(EmpId_id=empresaSel, UsuEmpRol='Sub-Admin').first()

        if(usuAdmin is not None):
            if (not solicitud.objects.filter( EmpId_id=empresaSel, FechaSolicitud=fecha, HoraSolicitud=hora, SolicitudActivo=True).exists()):
                nuevaSolicitud = solicitud(FechaSolicitud=fecha, HoraSolicitud=hora, SeConcreto=False, SolicitudActivo=True, UsuAdminResponsable_id=usuAdmin.id, UsuId_id=request.user.id, EmpId_id=empresaSel )
                nuevaSolicitud.save()
                messages.success(request, 'La solicitud para la empresa ' + empresaSeleccion.EmpRazonSocial + ' con fecha '+ fecha + ' y hora ' +hora + ' fue creada exitosamente.',extra_tags='alert alert-success')

#bloque que envía el correo de confirmación
                titulo_email = "Confirmación de cita de @gen-date"
                nombre_empresa = empresaSeleccion.EmpRazonSocial
                direccion = empresaSeleccion.EmpDirCalle
                numero_puerta = empresaSeleccion.EmpDirNum
                esquina = empresaSeleccion.EmpDirEsquina
                telefono = empresaSeleccion.EmpTelefono
                destinatario_mensaje = request.user.email

                email_body = """\
                    <html>
                    <head></head>
                    <body>
                    <h3>Hemos reservado su turno en el servicio:</h3>
                    <b><i>%s</i></b>
                    <p>para el %s a la hora %s </p>
                    <h5>Te recordamos la dirección : </h5>
                    %s %s esquina %s
                    <p>Tel : %s</p>
                    <p>Gracias por elegirnos...</p>
                    <i>En <b>@gen-date<b>... Simplificamos Tu Vida</i>
                    </body>
                    </html>
                    """ % (nombre_empresa, fecha, hora, direccion, numero_puerta, esquina, telefono )
                email = EmailMessage(titulo_email, email_body, to=[destinatario_mensaje])
                email.content_subtype = "html" # this is the crucial part 
                email.send()

            else:
                messages.error(request, 'Ya existe una solicitud para esa hora.', extra_tags='alert alert-danger')
        else:
            messages.error(request, 'No existe usuario administrador para la empresa seleccionada.', extra_tags='alert alert-danger')
        return redirect('/')
    return render(request, 'cuenta/aceptarSolicitud.html',context)

@login_required(login_url='login')
def modificarDatos(request):
    usuario = User.objects.get(id=request.user.id)
    form = FormularioModificarUsuario(instance=usuario)

    if request.method == 'POST':
        form = FormularioModificarUsuario(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Los datos fueron modificados con exito.' ,extra_tags='alert alert-success')
            return redirect('/')

    context = {"form": form}
    return render(request, 'cuenta/modificarDatos.html', context)

@login_required(login_url='login')
def bajaSolicitud(request, solicitudSel):
    solicitudes = solicitud.objects.filter(id=solicitudSel).first()

    if request.method == 'POST':
        solicitudes.SolicitudActivo = False
        solicitudes.save()
        messages.success(request, 'La solicitud ha sido dado de baja con exito.' ,extra_tags='alert alert-warning')

#bloque que envía el correo de anulación
        titulo_email = "Anulación de cita de @gen-date"
        num_empresa = solicitudes.EmpId_id
#me paro en la fila según filtro EmpId
        nempresa = empresa.objects.filter(EmpId=num_empresa).first()
#parado en esa fila tomo el campo EmpRazonSocial (nombre de la empresa)
        nombre_empresa = nempresa.EmpRazonSocial
        telefono = empresa.objects.filter(EmpId=num_empresa).first().EmpTelefono
        destinatario_mensaje = request.user.email

        email_body = """\
            <html>
            <head></head>
            <body>
            <h3>Porque así lo pediste ... </h3>
            <h3>Hemos Cancelado el turno en el servicio:</h3>
            <b><i>%s</i></b>
            <p>para el %s a la hora %s </p>
            <p>Tel : %s</p>
            <p>Gracias por elegirnos...</p>
            <i>En <b>@gen-date<b>... Simplificamos Tu Vida</i>
            </body>
            </html>
            """ % (nombre_empresa, solicitudes.FechaSolicitud, solicitudes.HoraSolicitud, telefono )
        email = EmailMessage(titulo_email, email_body, to=[destinatario_mensaje])
        email.content_subtype = "html" # this is the crucial part 
        email.send()

        return redirect('/')

    context = {'solicitud': solicitudes}
    return render(request, 'cuenta/bajaSolicitud.html', context)

@login_required(login_url='login')
def bajaSistema(request):
    if request.method == 'POST':
        request.user.is_active = False
        request.user.save()
        return redirect('logout')

    return render(request, 'cuenta/bajaSistema.html')

def quienesSomos(request):
    return render(request, 'cuenta/quienesSomos.html')

def mision(request):
    return render(request, 'cuenta/mision.html')

def contacto(request):
    return render(request, 'cuenta/contacto.html')


@login_required(login_url='login')
@solo_admin_grupo
def crearEmpresa(request):
    form = FormularioEmpresa()
    if request.method == 'POST':
        form = FormularioEmpresa(request.POST, request.FILES)
        if form.is_valid():
            # Creamos empresa
            empresaForm = form.save()
            if(empresaForm is not None):
                messages.success(request, 'La cuenta ' + empresaForm.EmpRazonSocial + ' fue creada exitosamente.',extra_tags='alert alert-success')
                
                # Asignamos usuario Admin a la empresa
                nuevoAdminEmpresa = usuariosEmpresa(UsuId=request.user, EmpId=empresaForm, UsuEmpRol='Admin', UsuEmpActivo=True)
                nuevoAdminEmpresa.save()

                # Creamos horario cerrado para la empresa
                nuevoHorario = horario(EmpId=nuevoAdminEmpresa.EmpId, LunesDesde=None, LunesHasta=None, MartesDesde=None, MartesHasta=None, MiercolesDesde=None, MiercolesHasta=None, JuevesDesde=None, JuevesHasta=None, ViernesDesde=None, ViernesHasta=None, SabadoDesde=None, SabadoHasta=None, DomingoDesde=None, DomingoHasta=None)
                nuevoHorario.save()

                # En caso que sea la primera empresa, dejamos seleccion 
                empresas = usuariosEmpresa.objects.filter(UsuId=request.user.id, UsuEmpActivo=True)
                if( empresas.count() == 1 ):
                    request.session['empresaSel'] = empresas.first().EmpId_id
                    request.session['empresaSelNombre'] = empresas.first().EmpId.EmpRazonSocial
                    request.session['empresaMultiple'] = False
                    request.session['empresaSelRol'] = empresas.first().UsuEmpRol
                else:
                    request.session['empresaMultiple'] = True

            return redirect('administrador')

    context = {'form': form}
    return render(request, 'cuenta/crearEmpresa.html', context)

@login_required(login_url='login')
@solo_admin_empresa
@validacion_cant_empresas # unicamente puede acceder a seleccion si cantidad > 1
def seleccionEmpresa(request):
    if request.method == 'POST':
        empresaNum = request.POST.get('empId')
        empresaSel = usuariosEmpresa.objects.filter(UsuId=request.user.id, EmpId=empresaNum, UsuEmpActivo=True).first()
        if(empresaSel is not None):
            request.session['empresaSel'] = empresaSel.EmpId_id
            request.session['empresaSelNombre'] = empresaSel.EmpId.EmpRazonSocial
            request.session['empresaSelRol'] = empresaSel.UsuEmpRol
        
        return redirect('administrador')

    empresas = usuariosEmpresa.objects.filter(UsuId=request.user.id, UsuEmpActivo=True)
    return render(request, 'cuenta/seleccionEmpresa.html', {'empresas': empresas})

@login_required(login_url='login')
@solo_admin_empresa
def modificarEmpresa(request):
    context={}
    if (request.session['empresaSel'] is not None):
        empresaModificar = empresa.objects.get(EmpId=request.session['empresaSel'])
        form= FormularioEmpresa(instance=empresaModificar)
        context={'form': form}
        if request.method == 'POST': 

            form = FormularioEmpresa(request.POST, request.FILES, instance=empresaModificar)
            if form.is_valid(): 
                form.save()
                messages.success(request, 'Empresa modificada con exito.' ,extra_tags='alert alert-success')
                return redirect('/')

    return render(request, 'cuenta/modificarEmpresa.html', context)

@login_required(login_url='login')
@solo_admin_empresa
def altaEmpleado(request):
    context={}
    if (request.session['empresaSel'] is not None):
        empresaSel = empresa.objects.get(EmpId=request.session['empresaSel'])

        if request.method == 'POST':
            usuId = request.POST.get('inputUsuAdminId')
            if(usuId is not None):
                if(es_numerico(usuId)):
                    
                    usuarioSel = User.objects.filter(id=usuId, is_active=True).first()

                    if(usuarioSel is not None):
                        # Buscamos si existe en la usuariosEmpresa
                        existeAdminEmpresa = usuariosEmpresa.objects.filter(UsuId=usuarioSel, EmpId=empresaSel).first()

                        if (existeAdminEmpresa is None):
                            nuevoAdminEmpresa = usuariosEmpresa(UsuId=usuarioSel, EmpId=empresaSel, UsuEmpRol='Sub-Admin', UsuEmpActivo=True)
                            nuevoAdminEmpresa.save()
                            messages.error(request, 'Se agregó el empleado '+ str(usuarioSel) + ' a la empresa: ' +  str(empresaSel),extra_tags='alert alert-success')
                            return redirect('/')
                        
                        else:
                            existeAdminEmpresa = usuariosEmpresa.objects.filter(UsuId=usuarioSel, EmpId=empresaSel, UsuEmpActivo=False).first()
                            
                            if existeAdminEmpresa is not None:
                                existeAdminEmpresa.UsuEmpActivo = True
                                existeAdminEmpresa.save()
                                messages.error(request, 'Se agregó el empleado '+ str(usuarioSel) + ' a la empresa: ' +  str(empresaSel),extra_tags='alert alert-success')
                                return redirect('/')
                            else:
                                messages.error(request, 'Ocurrió un error al intentar agregar el empleado a la empresa (Ya existe Administrador en la Empresa).' ,extra_tags='alert alert-warning')
                                return redirect('/')  

                    else:
                        messages.error(request, 'Ocurrió un error al intentar agregar el empleado a la empresa (UsuId no valido).' ,extra_tags='alert alert-warning')
                        return redirect('/')    
                else:
                    messages.error(request, 'Ocurrió un error al intentar agregar el empleado a la empresa (UsuId: NaN).' ,extra_tags='alert alert-warning')
                    return redirect('/')
            else:
                messages.error(request, 'Ocurrió un error al intentar agregar el empleado a la empresa (UsuId no puede ser vacio).' ,extra_tags='alert alert-warning')
                return redirect('/')

    return render(request, 'cuenta/altaEmpleado.html', context)

@login_required(login_url='login')
@solo_admin
def verAgendaEmpresa(request):
    solicitudes={}
    if (request.session['empresaSel'] is not None):
        solicitudes = solicitud.objects.filter(EmpId=request.session['empresaSel'], FechaSolicitud__gte=datetime.date.today(), SolicitudActivo=True)
    return render(request, 'cuenta/verAgendaEmpresa.html', {'solicitudes': solicitudes})


@login_required(login_url='login')
@solo_admin_empresa
def modificarHorarios(request):
    context={}
    if (request.session['empresaSel'] is not None):
        empresaHorario = horario.objects.filter(EmpId=request.session['empresaSel']).first()
        #print(empresaHorario)

        form = FormularioHorarios(instance=empresaHorario)

        dias = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes","Sabado","Domingo"]

        context={'form': form, 'dias': dias}
        
        if request.method == 'POST': 
            form = FormularioHorarios(request.POST, instance=empresaHorario)
            if form.is_valid(): 


                form.save()
                messages.success(request, 'Horario modificado con exito.' ,extra_tags='alert alert-success')
                return redirect('/')

    return render(request, 'cuenta/modificarHorarios.html', context)



@login_required(login_url='login')
@solo_admin_empresa
def bajaEmpresa(request):
    if (request.session['empresaSel'] is not None):
        bajaEmpresa = empresa.objects.filter(EmpId=request.session['empresaSel']).first()
        if request.method == 'POST':
            bajaEmpresa.EmpActivo = False
            bajaEmpresa.save()
            
            UsuEmp = usuariosEmpresa.objects.filter(EmpId=request.session['empresaSel'])
            for i in UsuEmp:
                i.UsuEmpActivo = False
                i.save()
           
            empresaSel = empresaPorDefecto(request)
            
            if(empresaSel is not None):
                request.session['empresaSel'] = empresaSel.EmpId_id
                request.session['empresaSelNombre'] = empresaSel.EmpId.EmpRazonSocial
                request.session['empresaMultiple'] = empresaMultiple(request)
                request.session['empresaSelRol'] = empresaSel.UsuEmpRol
            else:
                request.session['empresaSel'] = None
                request.session['empresaSelNombre'] = None
                request.session['empresaMultiple'] = None
                request.session['empresaSelRol'] = None

            messages.error(request, 'Se dió de baja correctamente la empresa',extra_tags='alert alert-success')
            return redirect('/')

    return render(request, 'cuenta/bajaEmpresa.html')


@login_required(login_url='login')
@solo_admin_empresa
def bajaEmpleado(request):
    usuariosEmp={}
    if (request.session['empresaSel'] is not None):
        usuariosEmp = usuariosEmpresa.objects.filter(EmpId=request.session['empresaSel'], UsuEmpRol="Sub-Admin", UsuEmpActivo=True)
        print(usuariosEmp)

    return render(request, 'cuenta/bajaEmpleado.html', {'usuariosEmp': usuariosEmp})

@login_required(login_url='login')
@solo_admin_empresa
def bajaEmpleadoConfirmar(request, UsuId):
    usuario={}
    if (request.session['empresaSel'] is not None):
        usuario = User.objects.filter(id=UsuId).first()
        if request.method == 'POST': 
            usuEmp = usuariosEmpresa.objects.filter(UsuEmpRol='Sub-Admin', EmpId=request.session['empresaSel'], UsuId=UsuId).first()
            usuEmp.UsuEmpActivo = False
            usuEmp.save()

            messages.success(request, 'Empleado dado de baja con exito.' ,extra_tags='alert alert-success')
            return redirect('/')

    return render(request, 'cuenta/bajaEmpleadoConfirmar.html', {'usuario': usuario})

@api_view(['GET'])
def apiList(request):
    api_urls = {
        'verAgendaV1':'/verAgendaV1/',
        'getAllRubrosV1':'/getAllRubrosV1/',
        'servicioListaV1':'/servicioListaV1/',
        'elegirServicioV1':'/elegirServicioV1/<str:rubro>/',
        'elegirHorarioV1':'/elegirHorarioV1/<str:empresaSel>/<str:fechaSel>',
        }
    return Response(api_urls)

@api_view(['GET'])
def getAllRubrosV1(request):
    rubros = rubro.objects.all()
    serializer = rubroSerializer(rubros, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getAllEmpresasV1(request):
    servicios = empresa.objects.all()
    serializer = elegirServicioSerializer(servicios, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def elegirServicioV1(request, rubro):
    servicios = (empresa.objects.filter(EmpRubro1=rubro) & empresa.objects.filter(EmpActivo=True)) | (empresa.objects.filter(EmpRubro2=rubro) & empresa.objects.filter(EmpActivo=True))
    serializer = elegirServicioSerializer(servicios, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getHorarioSolicitudEmpresaPorFechaV1(request, empresaSel, fechaSel):
    horarioEmpresa = horario.objects.filter(EmpId=empresaSel).first()
    solicitudesSet = set(solicitud.objects.filter(FechaSolicitud=fechaSel, EmpId=empresaSel, SolicitudActivo=True).values_list('HoraSolicitud', flat=True))

    solicitudes = set()
    for i in solicitudesSet:
        solicitudes.add(i.strftime("%H:%M"))

    desdeHasta = ["Desde", "Hasta"]
    dias = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes","Sabado","Domingo"]
    fecha = datetime.datetime.strptime(fechaSel, "%Y-%m-%d").date()
    numDia = fecha.weekday()

    horarioDesde = getattr(horarioEmpresa, dias[numDia]+desdeHasta[0])
    horarioHasta = getattr(horarioEmpresa, dias[numDia]+desdeHasta[1])

    listaHorarios = []
    listaHorariosVencidos = []

    if horarioDesde is not None and horarioHasta is not None:
        inicio = datetime.datetime.now().replace(hour=horarioDesde.hour, minute=horarioDesde.minute, second=horarioDesde.second)
        fin = datetime.datetime.now().replace(hour=horarioHasta.hour, minute=horarioHasta.minute, second=horarioHasta.second)
        listaHorarios = [ dt.strftime('%H:%M') for dt in rango_horas(inicio, fin, timedelta(minutes=30)) ]

        if fechaSel == str(date.today()) :
            fin = datetime.datetime.now() + timedelta(minutes=59)
            listaHorariosVencidos = [ dt.strftime('%H:%M') for dt in rango_horas(inicio, fin, timedelta(minutes=30)) ]

    res = {"Horario": [], "Solicitudes": [], "HorariosVencidos": []}
 
    for idx in range(len(listaHorarios)):
        res["Horario"].append(listaHorarios[idx])

    for idx in range(len(solicitudes)):
        res["Solicitudes"].append(solicitudes[idx])   

    for idx in range(len(listaHorariosVencidos)):
        res["HorariosVencidos"].append(listaHorariosVencidos[idx])   

    return Response(json.dumps(res))