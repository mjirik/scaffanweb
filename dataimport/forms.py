from django import forms
from .models import ServerDataFileName


class ImageQuatroForm(forms.ModelForm):
    class Meta:
        model = ServerDataFileName
        fields = ('description', 'imagefile', "annotationfile")