import json
from django.http import Http404, JsonResponse
from cuenta.models import User
from cuenta.utils import es_numerico

def obtenerUsuario(request):
    if request.is_ajax():
        usuAdmin = request.GET['usuAdmin']

        usuarioEmpSel = None
        data = None
        if(es_numerico(usuAdmin)):
            usuarioEmpSel = User.objects.filter(id=usuAdmin, is_active=True).first()

        if(usuarioEmpSel is not None):
                data = list(User.objects.values_list('id','username','email','first_name','last_name').get(id=usuAdmin, is_active=True))
        else:
            usuarioEmpSel = User.objects.filter(username=usuAdmin, is_active=True).first()

            if(usuarioEmpSel is not None):
                    data = list(User.objects.values_list('id','username','email','first_name','last_name').filter(username=usuAdmin, is_active=True).first())
            else:
                usuarioEmpSel = User.objects.filter(email=usuAdmin, is_active=True).first()

                if(usuarioEmpSel is not None):
                        data = list(User.objects.values_list('id','username','email','first_name','last_name').filter(email=usuAdmin, is_active=True).first())
            
        return JsonResponse({'data': data})
    else:
        raise Http404

