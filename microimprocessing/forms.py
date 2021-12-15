from django import forms
from .models import ServerDataFileName, Tag
from loguru import logger


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

class QueryForm(forms.Form):
    your_name = forms.CharField(label='Your name', max_length=100)


class ScaffanParameters(forms.Form):
    # renewal_date = forms.DateField(help_text="Enter a date between now and 4 weeks (default 3).")
    # name = forms.CharField(disabled=True)
    # value = forms.CharField(help_text="Parameters to update")

    def __init__(self, *args, **kwargs):
         super(ScaffanParameters, self).__init__(*args, **kwargs)
         import scaffan.algorithm
         mainapp = scaffan.algorithm.Scaffan()
         parameters_as_cfg_string = mainapp.get_parameters_as_cfg_string()
         dct = mainapp.parameters_to_dict()
         # dynamic fields here ...
         # self.fields['plan_id'] = forms.CharField()
         for element in dct:
             logger.debug(f"element {element} {type(dct[element])}")
             if type(dct[element]) == bool:
                 self.fields[element] = forms.BooleanField(initial=dct[element])
             else:
                 self.fields[element] = forms.CharField(initial=dct[element])
