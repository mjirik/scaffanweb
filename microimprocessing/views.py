from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth import logout
from django.core.files.base import ContentFile
from .models import get_output_dir
from .forms import ImageQuatroForm
from pathlib import Path
from django.conf import settings
import sys
# pth = str(Path(__file__).parent.parent.parent / "scaffan")
# print(f"local scaffan path={pth}")
# sys.path.insert(0, pth)
# print(f"PATH={sys.path}")
import os.path as op
from loguru import logger
import numpy as np

from .models import ServerDataFileName, LobuleCoordinates, ExampleData

# Create your views here.

def index(request):
    # latest_question_list = ServerDataFileName.objects.order_by('-pub_date')[:5]
    # latest_filenames = ServerDataFileName.objects.all()
    latest_filenames = ServerDataFileName.objects.filter(owner=request.user).order_by("-uploaded_at")
    number_of_points = [
        len(LobuleCoordinates.objects.filter(server_datafile=serverfile))
        for serverfile in latest_filenames
    ]
    output_exists = [
        Path(serverfile.outputdir).exists()
        for serverfile in latest_filenames
    ]

    for serverfile in latest_filenames:
        if Path(serverfile.outputdir).exists():
            logger.debug(f"output exists: {serverfile.outputdir}")
            if not Path(get_zip_fn(serverfile)).exists():
                make_zip(serverfile)
                serverfile.process_started = False
                serverfile.save()

    # latest_filenames_short = [
    #     Path(fn.imagefile.path).name for fn in latest_filenames
    #     ]
    # template = loader.get_template('microimprocessing/index.html')
    context = {
        'latest_filenames': zip(latest_filenames, number_of_points, output_exists),
        # "n_points": number_of_points,
    }
    # return HttpResponse(template.render(context, request))
    return render(request, 'microimprocessing/index.html', context)
# def index(request):
#     return HttpResponse("Hello, world. You're at the polls index.")


def delete_file(request, filename_id):
    serverfile = get_object_or_404(ServerDataFileName, pk=filename_id)
    serverfile.delete()
    return redirect('/microimprocessing/')


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
        # return render(request, 'microimprocessing/detail.html', {'serverfile': serverfile})
        return redirect('/microimprocessing/')
    else:
        return render(request, 'microimprocessing/detail.html', {'serverfile': serverfile})
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
            return redirect('/microimprocessing/')
    else:
        form = ImageQuatroForm()
    return render(request, 'microimprocessing/model_form_upload.html', {
        'form': form
    })

def run_processing(request, pk):
    from django_q.tasks import async_task, result
    # import scaffan
    # import scaffan.algorithm
    # import scaffan.image
    serverfile:ServerDataFileName = get_object_or_404(ServerDataFileName, pk=pk)


    coords = LobuleCoordinates.objects.filter(server_datafile=serverfile)
    centers_mm = [[coord.x_mm, coord.y_mm] for coord in coords]

    logger.debug(coords)
    serverfile.outputdir = get_output_dir()
    serverfile.process_started = True
    serverfile.save()

    cli_params = [
        settings.CONDA_EXECUTABLE, "run", "-n", "scaffanweb", "python", "-m", "scaffan", "nogui",
        "-i", str(serverfile.imagefile.path),
        "-o", str(serverfile.outputdir),
    ]
    for coord in coords:
        cli_params.append("--seeds_mm")
        cli_params.append(str(coord.x_mm))
        cli_params.append(str(coord.y_mm))



    logger.debug(f"adding task to queue CLI params: {' '.join(cli_params)}")
    import subprocess
    myProc = subprocess.Popen(cli_params)
    # subprocess.run(cli_params)


    # to capture the output we'll need a pipe
    # from subprocess import PIPE
    # tid = async_task("subprocess.run", cli_params, stdout=PIPE)

    # logger.debug("before results")
    # res = result(tid, 500)
    # print the output
    # logger.debug(res)
    # settings.CONDA_EXECUTABLE

        # logger.warning("running python directly. set settings.PYTHON_EXECUTABLE")
        # mainapp = scaffan.algorithm.Scaffan()
        # mainapp.set_input_file(serverfile.imagefile.path)
        # mainapp.set_output_dir(serverfile.outputdir)
        # mainapp.run_lobuluses(seeds_mm=centers_mm)
    return redirect('/microimprocessing/')

def get_zip_fn(serverfile:ServerDataFileName):
    nm = str(Path(serverfile.imagefile.path).name)
    # prepare output zip file path
    pth_zip = serverfile.outputdir + nm + ".zip"
    return pth_zip

def make_zip(serverfile:ServerDataFileName):
    pth_zip = get_zip_fn(serverfile)
    import shutil
    # remove last letters.because of .zip is added by make_archive
    shutil.make_archive(pth_zip[:-4], "zip", serverfile.outputdir)

    serverfile.processed = True
    pth_rel = op.relpath(pth_zip, settings.MEDIA_ROOT)
    serverfile.zip_file = pth_rel


    serverfile.save()


def make_thumbnail(serverfile:ServerDataFileName):
    import scaffan
    import scaffan.algorithm
    import scaffan.image
    logger.debug(f"serverfile={serverfile}")

    nm = str(Path(serverfile.imagefile.path).name)
    anim = scaffan.image.AnnotatedImage(serverfile.imagefile.path)


    full_view = anim.get_view(
        location=[0, 0], level=0, size_on_level=anim.get_slide_size()[::-1]
    )
    # pxsz_mm = float(self.get_parameter("Processing;Preview Pixelsize")) * 1000
    pxsz_mm = 0.02
    view_corner = full_view.to_pixelsize(pixelsize_mm=[pxsz_mm, pxsz_mm])
    img = view_corner.get_region_image(as_gray=False)
    pth = str(Path(settings.MEDIA_ROOT) / (nm + ".preview.jpg"))
    # pth = serverfile.outputdir + nm + ".preview.jpg"

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


def add_example_data(request):
    logger.debug("add example data")
    all = ExampleData.objects.all()
    for sample_image in all:
        logger.debug("add data")
        sdf = sample_image.server_datafile
        # sample_image.image
        logger.debug(f"add data as a copy of {sdf}")
        new_sdf = ServerDataFileName(
            owner=request.user,
            # imagefile=sdf.,
            preview=sdf.preview,
            description="Sample data",
            # preview=ContentFile(sdf.preview.read()),
        )
        # logger.debug(f"newsdf.owner{new_sdf.owner}, new_sdf.imagefile={new_sdf.imagefile}")
        # new_sdf.owner=request.user
        new_sdf.imagefile.save(Path(sdf.imagefile.name).name, ContentFile(sdf.imagefile.read()))
        make_thumbnail(new_sdf)
        # new_sdf.save()
        logger.debug(f"newsdf.owner{new_sdf.owner}, new_sdf.imagefile={new_sdf.imagefile}")

    return redirect('/microimprocessing/')


    # latest_filenames = ServerDataFileName.objects.filter(owner=request.user)

def logout_view(request):
    logout(request)
    # Redirect to a success page.
    return redirect('/')
