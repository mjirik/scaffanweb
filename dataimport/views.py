from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.template import loader
from .models import get_output_dir
from .forms import ImageQuatroForm
from pathlib import Path
from django.conf import settings
import sys
# pth = str(Path(__file__).parent.parent.parent / "scaffan")
# print(f"local scaffan path={pth}")
# sys.path.insert(0, pth)
# print(f"PATH={sys.path}")
import scaffan
import scaffan.algorithm
import scaffan.image
import os.path as op
from loguru import logger

from .models import ServerDataFileName

# Create your views here.

def index(request):
    # latest_question_list = ServerDataFileName.objects.order_by('-pub_date')[:5]
    # latest_filenames = ServerDataFileName.objects.all()
    latest_filenames = ServerDataFileName.objects.filter(owner=request.user)
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
        form = ImageQuatroForm(request.POST, request.FILES,
                               # owner=request.user
                               )
        if form.is_valid():
            serverfile = form.save()
            # form.save()
            print(f"user id={request.user.id}")
            serverfile.owner = request.user
            serverfile.save()
            make_thumbnail(serverfile)
            # mainapp = scaffan.algorithm.Scaffan()
            # mainapp.set_input_file(serverfile.imagefile.path)
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


def make_thumbnail(serverfile:ServerDataFileName):

    nm = str(Path(serverfile.imagefile.path).name)
    anim = scaffan.image.AnnotatedImage(serverfile.imagefile.path)


    full_view = anim.get_view(
        location=[0, 0], level=0, size_on_level=anim.get_slide_size()[::-1]
    )
    # pxsz_mm = float(self.get_parameter("Processing;Preview Pixelsize")) * 1000
    pxsz_mm = 0.1
    view_corner = full_view.to_pixelsize(pixelsize_mm=[pxsz_mm, pxsz_mm])
    img = view_corner.get_region_image(as_gray=False)
    pth = serverfile.outputdir + nm + ".thumbnail.jpg"
    # pth = serverfile.imagefile.path + ".thumbnail.jpg"
    logger.debug("thumbnail path")
    logger.debug(pth)
    pth_rel = op.relpath(pth, settings.MEDIA_ROOT)
    logger.debug(pth_rel)
    serverfile.thumbnail = pth_rel
    import skimage.io
    skimage.io.imsave(pth, img[:,:,:3])
    serverfile.save()

