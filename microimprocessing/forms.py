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
         # parameters_as_cfg_string = mainapp.get_parameters_as_cfg_string()
         dct = mainapp.parameters_to_dict()
         # Remove parameters from Input and Output
         dct = {key: val for key, val in dct.items() if not key.startswith("Input;") and not key.startswith("Output;")}
         dct.pop("Processing;Show")
         dct.pop("Processing;Open output dir")

         # dynamic fields here ...
         # self.fields['plan_id'] = forms.CharField()
         for element in dct:
             logger.debug(f"element {element} {type(dct[element])}")
             p = mainapp.parameters.param(*element.split(";"))
             help_text = p.opts["tip"] if "tip" in p.opts else ""
             if type(dct[element]) == bool:
                 self.fields[element] = forms.BooleanField(initial=dct[element], required=False, help_text=help_text)
             else:
                 self.fields[element] = forms.CharField(initial=dct[element], required=False, help_text=help_text)
