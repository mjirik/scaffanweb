from django import forms
from .models import ServerDataFileName, Tag


class ImageQuatroForm(forms.ModelForm):
    # def __init__(self, *args, **kwargs):
    #     self.owner_user = kwargs.pop('owner', None)
    #     super(ImageQuatroForm, self).__init__(*args, **kwargs)
    class Meta:
        model = ServerDataFileName
        fields = ('description', 'imagefile', "annotationfile")

class TagForm(forms.ModelForm):
    # def __init__(self, *args, **kwargs):
    #     self.owner_user = kwargs.pop('owner', None)
    #     super(ImageQuatroForm, self).__init__(*args, **kwargs)
    class Meta:
        model = Tag
        fields = ('name', )
