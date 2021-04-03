from django.http import HttpResponse
from django.shortcuts import redirect
from cuenta.models import usuariosEmpresa, es_admin
# Decorador es una funcion que acepta a otra funcion como parametro
# Nos permite agregar otras funcionalidades antes de ejecutar una funcion


# Ejemplo de uso de usuario_noAutenticado:
# @usuario_noAutenticado arriba de la funcion loginPage (en views.py)
# Se va a ejecutar el bloque de codigo de abajo,
# y en caso de estar autenticado, redirige a home, sino ejecuta login
def usuario_noAutenticado(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        else:
            return view_func(request, *args, **kwargs)
    
    return wrapper_func


def usuarios_permitido(grupo_permitido=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):

            group = None
            if request.user.groups.exists():
                for group in request.user.groups.all():
                    if group.name in grupo_permitido:
                        return view_func(request, *args, **kwargs)

            return HttpResponse('No estas autorizado para ver esta pagina.')

        return wrapper_func
    return decorator

def solo_admin_empresa(view_func):
    def wrapper_func(request, *args, **kwargs):
        if 'empresaSel' in request.session:
            if (request.session['empresaSel'] is not None):
                usuEmp = usuariosEmpresa.objects.filter(UsuId=request.user.id, EmpId=request.session['empresaSel'], UsuEmpRol="Admin", UsuEmpActivo=True).first()
                if usuEmp is not None:
                    return view_func(request, *args, **kwargs)    
        return redirect('home')     

    return wrapper_func

def solo_admin_grupo(view_func):
    def wrapper_func(request, *args, **kwargs):
        group = None
        if request.user.groups.exists():
            for group in request.user.groups.all():
                if group.name == "Admin":
                    return view_func(request, *args, **kwargs)    
                  
        return redirect('home')     

    return wrapper_func

def solo_admin(view_func):
    def wrapper_func(request, *args, **kwargs):
        group = None
        if 'empresaSel' in request.session:
            if (request.session['empresaSel'] is not None):
                usuEmp = usuariosEmpresa.objects.filter(UsuId=request.user.id, UsuEmpActivo=True).first()
                if usuEmp is not None:
                    return view_func(request, *args, **kwargs)
        else:     
            return redirect('home')     

    return wrapper_func

def solo_usuario(view_func):
    def wrapper_func(request, *args, **kwargs):
        group = None
        if es_admin(request.user):
            if 'empresaSel' in request.session:
                if (request.session['empresaSel'] is not None):
                    usuEmp = usuariosEmpresa.objects.filter(UsuId=request.user.id, UsuEmpActivo=True).first()
                    if usuEmp is not None:
                        return redirect('administrador')     
            #return view_func(request, *args, **kwargs)   
                     
        return view_func(request, *args, **kwargs)         
            
    return wrapper_func

def usuarios_NoPermitido(grupo_NoPermitido=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):

            group = None
            if request.user.groups.exists():
                for group in request.user.groups.all():
                    if group.name in grupo_NoPermitido:
                        return HttpResponse('No estas autorizado para ver esta pagina.')

            return view_func(request, *args, **kwargs)
                
        return wrapper_func
    return decorator

def validacion_cant_empresas(view_func):
    def wrapper_func(request, *args, **kwargs):
        empresas = usuariosEmpresa.objects.filter(UsuId=request.user.id, UsuEmpActivo=True)

        if empresas is not None:
            if empresas.count() < 2:
                return redirect('administrador')     
                     
        return view_func(request, *args, **kwargs)         
            
    return wrapper_func