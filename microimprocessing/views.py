
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth import logout
from django.core.files.base import ContentFile
from .models import get_output_dir, Tag
from .forms import ImageQuatroForm, TagForm
from .tasks import make_thumbnail
from pathlib import Path
from django.conf import settings
from microimprocessing import models
import sys
# pth = str(Path(__file__).parent.parent.parent / "scaffan")
# print(f"local scaffan path={pth}")
# sys.path.insert(0, pth)
# print(f"PATH={sys.path}")
import os.path as op
from loguru import logger
import numpy as np

from .models import ServerDataFileName, LobuleCoordinates, ExampleData, User

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
        (Path(serverfile.outputdir) / "data.xlsx").exists()
        for serverfile in latest_filenames
    ]

    for serverfile in latest_filenames:
        if (Path(serverfile.outputdir) / "data.xlsx").exists():
            logger.debug(f"output exists: {serverfile.outputdir}")
            zip_fn = get_zip_fn(serverfile)
            if zip_fn:
                if not Path(zip_fn).exists():
                    make_zip(serverfile)
                    serverfile.process_started = False
                    serverfile.save()
    zip_exists = [
        Path(get_zip_fn(serverfile)).exists() if get_zip_fn(serverfile) else False
        for serverfile in latest_filenames
    ]

    fn, spreadsheet_url, name = models.get_common_spreadsheet_file(request.user)
    spreadsheet_exists = fn.exists()

    # latest_filenames_short = [
    #     Path(fn.imagefile.path).name for fn in latest_filenames
    #     ]
    # template = loader.get_template('microimprocessing/index.html')
    context = {
        'latest_filenames': zip(latest_filenames, number_of_points, output_exists, zip_exists),
        "spreadsheet_exists": spreadsheet_exists,
        "spreadsheet_url": spreadsheet_url,
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

def _preapare_xlsx_for_rendering(filename:Path):
    logger.debug(filename)
    df_html = None
    if filename.exists():
        import pandas as pd
        dfall = pd.read_excel(str(filename), sheet_name="Sheet1",
                              index=False,
                              # index_col=0
                              )
        key_candidate = ["SNI area prediction", "Skeleton length", "Branch number", "Dead ends number",
                         "Area", "Area unit", "Lobulus Perimeter",
                         "Annotation Center X [mm]", "Annotation Center Y [mm]",
                         "Scan Segmentation Empty Area [mm^2]", "Scan Segmentation Septum Area [mm^2]",
                         "Scan Segmentation Sinusoidal Area [mm^2]",
                         ]
        keys = [key for key in key_candidate if key in dfall.keys()]
        df = dfall[keys]
        df_html = df.to_html(classes="table table-hover", border=0)

    return df_html

def detail(request, filename_id):
    serverfile = get_object_or_404(ServerDataFileName, pk=filename_id)

    filename = Path(serverfile.outputdir) / "data.xlsx"

        # import glob
        # image_list = glob.glob(str(Path(serverfile.outputdir) / "lobulus_*.png"))

    df_html = _preapare_xlsx_for_rendering(filename)
    image_list = []
    return render(request, 'microimprocessing/detail.html',
                  {'serverfile': serverfile, 'df_html':df_html, "image_list":image_list})

def common_spreadsheet(request):

    filename,url,_ = models.get_common_spreadsheet_file(request.user)
    # serverfile = get_object_or_404(ServerDataFileName, pk=filename_id)
    # filename = Path(serverfile.outputdir) / "data.xlsx"

    # import glob
    # image_list = glob.glob(str(Path(serverfile.outputdir) / "lobulus_*.png"))

    df_html = _preapare_xlsx_for_rendering(filename)
    image_list = []
    return render(request, 'microimprocessing/detail.html',
                  {
                      'serverfile': "Common Spreadsheet",
                      'df_html':df_html,
                      "image_list":image_list,
                      "spreadsheet_url":url}
                  )


def set_lobules_seeds(request, filename_id):
    serverfile = get_object_or_404(ServerDataFileName, pk=filename_id)
    if not serverfile.preview:
        make_thumbnail(serverfile)
    if request.method == 'POST':
        LobuleCoordinates.objects.filter(server_datafile=serverfile).delete()
        print("post recived")
        print(request.POST)
        postDict = dict(request.POST)
        if "x" in postDict:
            xstrs = postDict["x"]
            ystrs = postDict["y"]
            xystrs = list(zip(xstrs, ystrs))
            logger.debug(f"xstrs={xstrs}")
            logger.debug(f"ystrs={ystrs}")
            logger.debug(f"xystrs={xystrs}")
            for xystr in xystrs:
                logger.debug(f"Addeding new point" )
                x_mm = float(xystr[0]) * serverfile.preview_pixelsize_mm
                y_mm = float(xystr[1]) * serverfile.preview_pixelsize_mm
                coords = LobuleCoordinates(x_mm=x_mm, y_mm=y_mm, server_datafile=serverfile)
                coords.save()
                logger.debug(f"Added new point={x_mm},{y_mm}")
        # return render(request, 'microimprocessing/set_lobules_seeds.html', {'serverfile': serverfile})
        return redirect('/microimprocessing/')
    else:
        return render(request, 'microimprocessing/set_lobules_seeds.html', {'serverfile': serverfile})
    # return HttpResponse("You're looking at question %s." % question_id)


def model_form_upload(request):
    if request.method == 'POST':
        form = ImageQuatroForm(request.POST, request.FILES,
                               # owner=request.user
                               )
        if form.is_valid():
            from django_q.tasks import async_task
            serverfile = form.save()
            print(f"user id={request.user.id}")
            serverfile.owner = request.user
            serverfile.save()
            async_task('microimprocessing.tasks.make_thumbnail', serverfile,
                       # hook='tasks.email_report'
                       )
            return redirect('/microimprocessing/')
    else:
        form = ImageQuatroForm()
    return render(request, 'microimprocessing/model_form_upload.html', {
        'form': form
    })

def create_tag(request):
    if request.method == 'POST':
        form = TagForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data['name']
            objs = Tag.objects.filter(name=name)
            if len(objs) == 0:
                tag = form.save()
            else:
                tag = objs[0]
            return redirect('/microimprocessing/')
    else:
        form = TagForm

    return render(request, 'microimprocessing/model_form_upload.html', {
        'form': form
    })


def run_processing(request, pk):
    from django_q.tasks import async_task, result
    # import scaffan
    # import scaffan.algorithm
    # import scaffan.image
    serverfile:ServerDataFileName = get_object_or_404(ServerDataFileName, pk=pk)


    # import subprocess
    # myProc = subprocess.Popen(cli_params)


    # to capture the output we'll need a pipe
    # from subprocess import PIPE
    # tid = async_task("subprocess.run", cli_params, hook="microimprocessing.views.make_thumbnail")
    serverfile.process_started = True
    serverfile.outputdir = get_output_dir()
    serverfile.save()

    tid = async_task('microimprocessing.tasks.run_processing', serverfile
                     # hook="microimprocessing.views.make_thumbnail"
               # hook='tasks.email_report'
               )

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
    logger.debug(f"serverfile.imagefile={serverfile.imagefile.name}")
    if not serverfile.imagefile.name:
        logger.debug(f"No file uploaded for {serverfile.imagefile}")
        return None
        # file is not uploaded

    nm = str(Path(serverfile.imagefile.path).name)
    # prepare output zip file path
    pth_zip = serverfile.outputdir + nm + ".zip"
    return pth_zip

def make_zip(serverfile:ServerDataFileName):
    pth_zip = get_zip_fn(serverfile)
    if pth_zip:
        import shutil
        # remove last letters.because of .zip is added by make_archive
        shutil.make_archive(pth_zip[:-4], "zip", serverfile.outputdir)

        serverfile.processed = True
        pth_rel = op.relpath(pth_zip, settings.MEDIA_ROOT)
        serverfile.zip_file = pth_rel
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


def create_report(request):
    from django_q.tasks import async_task
    async_task('microimprocessing.tasks.create_html_report',
            request.user,
            # hook='tasks.email_report'
               )
    return redirect('/microimprocessing/')
