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
import numpy as np

from .models import ServerDataFileName, LobuleCoordinates

# Create your views here.

def index(request):
    # latest_question_list = ServerDataFileName.objects.order_by('-pub_date')[:5]
    # latest_filenames = ServerDataFileName.objects.all()
    latest_filenames = ServerDataFileName.objects.filter(owner=request.user)
    number_of_points = [
        len(LobuleCoordinates.objects.filter(server_datafile=serverfile))
        for serverfile in latest_filenames
    ]
    # template = loader.get_template('dataimport/index.html')
    context = {
        'latest_filenames': zip(latest_filenames, number_of_points),
        # "n_points": number_of_points,
    }
    # return HttpResponse(template.render(context, request))
    return render(request, 'dataimport/index.html', context)
# def index(request):
#     return HttpResponse("Hello, world. You're at the polls index.")


def detail(request, filename_id):
    serverfile = get_object_or_404(ServerDataFileName, pk=filename_id)
    if request.method == 'POST':
        LobuleCoordinates.objects.filter(server_datafile=serverfile).delete()
        print("post recived")
        print(request.POST)
        postDict = dict(request.POST)
        xstrs = postDict["x"]
        ystrs = postDict["y"]
        xystrs = list(zip(xstrs, ystrs))
        print(f"xstrs={xstrs}")
        print(f"ystrs={ystrs}")
        logger.debug(xystrs)
        for xystr in xystrs:
            logger.debug(f"Addeding new point" )
            x_mm = float(xystr[0]) * serverfile.preview_pixelsize_mm
            y_mm = float(xystr[1]) * serverfile.preview_pixelsize_mm
            coords = LobuleCoordinates(x_mm=x_mm, y_mm=y_mm, server_datafile=serverfile)
            coords.save()
            logger.debug(f"Added new point={x_mm},{y_mm}")
        # return render(request, 'dataimport/detail.html', {'serverfile': serverfile})
        return redirect('/dataimport/')
    else:
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

    mainapp = scaffan.algorithm.Scaffan()
    mainapp.set_input_file(serverfile.imagefile.path)

    coords = LobuleCoordinates.objects.filter(server_datafile=serverfile)
    centers_mm = [[coord.x_mm, coord.y_mm] for coord in coords]
    logger.debug(coords)
    serverfile.outputdir = get_output_dir()
    serverfile.save()
    mainapp.set_output_dir(serverfile.outputdir)
    # _, ann_ids = mainapp.prepare_circle_annotations_from_points_mm(centers_mm)
    # mainapp.init_run()
    # mainapp.set_annotation_color_selection("#FF00FF") # magenta -> cyan
    # mainapp.set_annotation_color_selection("#00FFFF")
    # cyan causes memory fail
    # mainapp.set_parameter("Input;Lobulus Selection Method", "Color")
    # mainapp.set_annotation_color_selection("#FF0000")

    mainapp.run_lobuluses(seeds_mm=centers_mm)

    import shutil
    shutil.make_archive(serverfile.outputdir, "zip", serverfile.outputdir)


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
    pxsz_mm = 0.02
    view_corner = full_view.to_pixelsize(pixelsize_mm=[pxsz_mm, pxsz_mm])
    img = view_corner.get_region_image(as_gray=False)
    pth = serverfile.outputdir + nm + ".preview.jpg"
    # pth = serverfile.imagefile.path + ".thumbnail.jpg"
    logger.debug("thumbnail path")
    logger.debug(pth)
    pth_rel = op.relpath(pth, settings.MEDIA_ROOT)
    logger.debug(pth_rel)
    serverfile.preview = pth_rel
    serverfile.preview_pixelsize_mm = pxsz_mm
    import skimage.io
    logger.debug(f"img max: {np.max(img)}, img.dtype={img.dtype}")
    if img.dtype != np.uint8:
        img = (img*255).astype(np.uint8)
    skimage.io.imsave(pth, img[:,:,:3])

    serverfile.save()

