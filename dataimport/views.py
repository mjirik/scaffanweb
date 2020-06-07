from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.template import loader
from .models import get_output_dir
from .forms import ImageQuatroForm
from pathlib import Path
import sys
# pth = str(Path(__file__).parent.parent.parent / "scaffan")
# print(f"local scaffan path={pth}")
# sys.path.insert(0, pth)
# print(f"PATH={sys.path}")
import scaffan
import scaffan.algorithm

from .models import ServerDataFileName

# Create your views here.

def index(request):
    # latest_question_list = ServerDataFileName.objects.order_by('-pub_date')[:5]
    latest_filenames = ServerDataFileName.objects.all()
    # template = loader.get_template('dataimport/index.html')
    context = {
        'latest_filenames': latest_filenames,
    }
    # return HttpResponse(template.render(context, request))
    return render(request, 'dataimport/index.html', context)
# def index(request):
#     return HttpResponse("Hello, world. You're at the polls index.")


def detail(request, filename_id):
    serverfile = get_object_or_404(ServerDataFileName, pk=filename_id)
    return render(request, 'dataimport/detail.html', {'serverfile': serverfile})
    # return HttpResponse("You're looking at question %s." % question_id)


def model_form_upload(request):
    if request.method == 'POST':
        form = ImageQuatroForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # from . import imageprocessing
            # imageprocessing.quatrofile_processing()
            return redirect('/dataimport/')
    else:
        form = ImageQuatroForm()
    return render(request, 'dataimport/model_form_upload.html', {
        'form': form
    })

def run_processing(request, pk):
    serverfile:ServerDataFileName = get_object_or_404(ServerDataFileName, pk=pk)
    scaffan
    mainapp = scaffan.algorithm.Scaffan()


    mainapp.set_input_file(serverfile.imagefile.path)
    serverfile.outputdir.path = get_output_dir()
    serverfile.save()
    mainapp.set_output_dir(serverfile.outputdir.path)
    # mainapp.init_run()
    # mainapp.set_annotation_color_selection("#FF00FF") # magenta -> cyan
    # mainapp.set_annotation_color_selection("#00FFFF")
    # cyan causes memory fail
    mainapp.set_parameter("Input;Lobulus Selection Method", "Color")
    mainapp.set_annotation_color_selection("#FF0000")
    mainapp.run_lobuluses()
    serverfile.processed = True
    serverfile.save()
    return redirect('/dataimport/')
