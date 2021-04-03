from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from cuenta.models import empresa, horario


class FormularioCreacionUsuario(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','email', 'password1','password2','first_name','last_name']

class FormularioModificarUsuario(ModelForm):
    class Meta:
        model = User
        fields = ['first_name','last_name','email']

# Widget fecha
class InputFecha(forms.DateInput):
    input_type = 'date'

# Formulario, paso por parametro el widget que quiero utilizar
class FormularioElegirHorario(forms.Form):
    campo_fecha = forms.DateField(widget=InputFecha)


class FormularioEmpresa(ModelForm):
    class Meta:
        model = empresa
        fields = ['EmpRUT','EmpRazonSocial','EmpDirCalle','EmpDirEsquina','EmpDirNum', 'EmpTelefono','EmpDirEmail','EmpRubro1','EmpDescripcion', 'EmpImagen']

    def __init__(self, *args, **kwargs):
        super(FormularioEmpresa, self).__init__(*args, **kwargs)
        self.fields['EmpRUT'].widget.attrs={'class': 'form-control'}
        self.fields['EmpRazonSocial'].widget.attrs={'class': 'form-control'}
        self.fields['EmpDirCalle'].widget.attrs={'class': 'form-control'}
        self.fields['EmpDirEsquina'].widget.attrs={'class': 'form-control'}
        self.fields['EmpDirNum'].widget.attrs={'class': 'form-control'}
        self.fields['EmpTelefono'].widget.attrs={'class': 'form-control'}
        self.fields['EmpDirEmail'].widget.attrs={'class': 'form-control'}
        self.fields['EmpRubro1'].widget.attrs={'class': 'form-control'}
        self.fields['EmpDescripcion'].widget.attrs={'class': 'form-control'}
        self.fields['EmpImagen'].widget.attrs={'class': 'form-control-file'}


class FormularioHorarios(ModelForm):
    class Meta:
        model = horario
        fields = ['LunesDesde','LunesHasta','MartesDesde','MartesHasta','MiercolesDesde', 'MiercolesHasta','JuevesDesde','JuevesHasta','ViernesDesde', 'ViernesHasta','SabadoDesde', 'SabadoHasta','DomingoDesde', 'DomingoHasta']

    def __init__(self, *args, **kwargs):
        super(FormularioHorarios, self).__init__(*args, **kwargs)
        self.fields['LunesDesde'].widget.attrs={'class': 'form-control'}
        self.fields['LunesHasta'].widget.attrs={'class': 'form-control'}
        self.fields['MartesDesde'].widget.attrs={'class': 'form-control'}
        self.fields['MartesHasta'].widget.attrs={'class': 'form-control'}
        self.fields['MiercolesDesde'].widget.attrs={'class': 'form-control'}
        self.fields['MiercolesHasta'].widget.attrs={'class': 'form-control'}
        self.fields['JuevesDesde'].widget.attrs={'class': 'form-control'}
        self.fields['JuevesHasta'].widget.attrs={'class': 'form-control'}
        self.fields['ViernesDesde'].widget.attrs={'class': 'form-control'}
        self.fields['ViernesHasta'].widget.attrs={'class': 'form-control'}
        self.fields['SabadoDesde'].widget.attrs={'class': 'form-control'}
        self.fields['SabadoHasta'].widget.attrs={'class': 'form-control'}
        self.fields['DomingoDesde'].widget.attrs={'class': 'form-control'}
        self.fields['DomingoHasta'].widget.attrs={'class': 'form-control'}