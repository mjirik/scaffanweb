
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth import logout
from django.core.files.base import ContentFile
from .models import get_output_dir, Tag
from .forms import ImageQuatroForm, TagForm, ScaffanParameters
from .tasks import make_thumbnail, get_zip_fn, make_zip
from pathlib import Path
from django.conf import settings
from django.views.generic import ListView
from django.http import HttpResponse
from datetime import datetime
from microimprocessing import models, tasks
import sys
# pth = str(Path(__file__).parent.parent.parent / "scaffan")
# print(f"local scaffan path={pth}")
# sys.path.insert(0, pth)
# print(f"PATH={sys.path}")
import os.path as op
from loguru import logger
import numpy as np
import django_q
import glob
import os.path
import pprint

from .models import ServerDataFileName, LobuleCoordinates, ExampleData, User, GDriveImport


def index(request):
    # latest_question_list = ServerDataFileName.objects.order_by('-pub_date')[:5]
    # latest_filenames = ServerDataFileName.objects.all()
    hide_tags = request.session.get("hide_tags", [])
    show_tags = request.session.get("show_tags", [])
    logger.trace(f"hide_tags={hide_tags}")
    logger.trace(f"show_tags={show_tags}")
    logger.debug(f"Preparing index view for {request.user}")
    order_by = request.session.get("order_by", '-uploaded_at')
    order_by_items_input = [
        "uploaded_at",
        "started_at",
        "filename"
    ]

    order_by_items = []
    for field in order_by_items_input:
        if field == 'filename':
            title = "Filename"
        else:
            title = models.ServerDataFileName._meta.get_field(field).verbose_name.title()
        order_by_items.append([
            field,
            "▲ " + title,
            # "&#9650; " + title,
            field == order_by
        ])
        order_by_items.append([
            "-" + field,
            "▼ " + title,
            # "&#9660; " + title,
            ("-" + field) == order_by
        ])

    # logger.warning(order_by_items)
    logger.trace("getting filenames")
    qs_latest_filenames = ServerDataFileName.objects.filter(
        owner=request.user,
        ).exclude(
        tag__in=hide_tags
    )
    logger.trace("preparing tags")
    if len(show_tags) > 0:
        qs_latest_filenames = qs_latest_filenames.filter(tag__in=request.session.get("show_tags", []))

    if order_by == "filename":
        latest_filenames = sorted(qs_latest_filenames, key=lambda i: i.filename, reverse=False)
    elif order_by  == "-filename":
        latest_filenames = sorted(qs_latest_filenames, key=lambda i: i.filename, reverse=True)
    else:
        latest_filenames = qs_latest_filenames.order_by(order_by)

    logger.trace("getting number of points ...")
    number_of_points = [
        len(LobuleCoordinates.objects.filter(server_datafile=serverfile))
        for serverfile in latest_filenames
    ]
    output_exists = [
        (Path(serverfile.outputdir) / "data.xlsx").exists()
        for serverfile in latest_filenames
    ]

    # for serverfile in latest_filenames:
    #     if (Path(serverfile.outputdir) / "data.xlsx").exists():
    #         logger.debug(f"output exists: {serverfile.outputdir}")
    #         zip_fn = get_zip_fn(serverfile)
    #         if zip_fn:
    #             if not Path(zip_fn).exists():
    #                 make_zip(serverfile)
    #                 serverfile.process_started = False
    #                 serverfile.save()
    logger.trace("check zip exists")
    zip_exists = [
        Path(get_zip_fn(serverfile)).exists() if get_zip_fn(serverfile) else False
        for serverfile in latest_filenames
    ]
    logger.trace("collecting possible errors")
    file_error = [
        _find_error(serverfile)[0]
        # None if Path(serverfile.imagefile.path).exists() else "File not found on the server" if get_zip_fn(serverfile) else False
        for serverfile in latest_filenames
    ]
    logger.trace("setting tags...")
    files_tags = [serverfile.tag_set.all()
        for serverfile in latest_filenames
    ]

    logger.trace("getting common spreadsheet file")
    fn, spreadsheet_url, name = models.get_common_spreadsheet_file(request.user)
    spreadsheet_exists = fn.exists()

    # latest_filenames_short = [
    #     Path(fn.imagefile.path).name for fn in latest_filenames
    #     ]
    # template = loader.get_template('microimprocessing/index.html')
    # if request.user in gdriveimport.user.all():

    logger.trace("preparing gdrive import")
    user_has_gdrive_import = (len(models.GDriveImport.objects.filter(user=request.user)) > 0)

    user_tags = [
        (
            tag,
            "show" if tag.id in request.session.get("show_tags", []) else
            "hide" if tag.id in request.session.get("hide_tags", []) else
            "ignore"
        ) for tag in  request.user.tag_set.all()]
    context = {
        'latest_filenames': zip(
            latest_filenames,
            number_of_points,
            output_exists,
            zip_exists,
            files_tags,
            file_error
        ),
        "spreadsheet_exists": spreadsheet_exists,
        "spreadsheet_url": spreadsheet_url,
        "user_tags": user_tags,
        "user_has_gdrive_import": user_has_gdrive_import,
        "order_by": order_by,
        "order_by_items": order_by_items,
        # "n_points": number_of_points,
    }
    # return HttpResponse(template.render(context, request))
    logger.debug("Index view almost finished. Rendering...")
    return render(request, 'microimprocessing/index.html', context)
# def index(request):
#     return HttpResponse("Hello, world. You're at the polls index.")


def create_and_download_zip(request, filename_id):
    serverfile = get_object_or_404(ServerDataFileName, pk=filename_id)
    zip_fn = get_zip_fn(serverfile)
    if zip_fn:
        make_zip(serverfile)
        serverfile.process_started = False
        serverfile.save()
    return redirect(serverfile.zip_file.url)


def _find_error(serverfile:ServerDataFileName):

    msg = ''
    if (not Path(serverfile.imagefile.path).exists()) and get_zip_fn( serverfile):
        msg += "File not found on the server. "
        # is_failed = [fn in first_arg_of_failed_tasks for fn in latest_filenames]
    # tasks_of_file = [tsk for tsk in django_q.models.Task.objects.all().order_by('-started') if
    #                      ((len(tsk.args) > 0) and (tsk.args[0] == serverfile))]

    # if len(tasks_of_file) > 0:
    #     last_task = tasks_of_file[0]
    if serverfile.last_task_uuid:
        last_task = django_q.models.Task.get_task(serverfile.last_task_uuid)
        if last_task is None:
            msg += f"Task {serverfile.last_task_uuid} not found. "
        elif last_task.success:
            pass
        else:
            msg += f"Failed task. Func: {last_task.func}, Short result: {last_task.short_result}"
    else:
        last_task = None



    return msg, last_task


def delete_file(request, filename_id):
    serverfile = get_object_or_404(ServerDataFileName, pk=filename_id)
    serverfile.delete()
    return redirect('/microimprocessing/')


# class GenericFileListView(ListView):
#     # not used
#     model = ServerDataFileName
#
#     def head(self, *args, **kwargs):
#         last_book = self.get_queryset().latest('upladed_at')
#         response = HttpResponse()
#         # RFC 1123 date format
#         response['Last-Modified'] = last_book.publication_date.strftime('%a, %d %b %Y %H:%M:%S GMT')
#         return response
#

def force_update(request):
    """
    Used to generate few things automatically. Usually used for debug.
    :param request:
    :return:
    """
    from django_q.tasks import async_task
    # logger.debug(f"parameters={parameters}")
    tid = async_task(
        'microimprocessing.tasks.force_update_task',
        # hook="microimprocessing.views.make_thumbnail"
        # hook='microimprocessing.tasks.finish_processing',
    )

    return redirect('/microimprocessing/')


def file_log(request, filename_id):
    serverfile = get_object_or_404(ServerDataFileName, pk=filename_id)
    msg, task = _find_error(serverfile)
    logger.debug(f"task={task}")
    logger.debug(f"serverfile.last_task_uuid={serverfile.last_task_uuid}")
    key_value = {}
    if task:
        key_value = {
            'Id': task.id,
            'Name': task.name,
            'Func': task.func,
            'Hook': task.hook,
            'Args': ", ".join(map(str, task.args)),
            'Kwargs': ", ".join(map(str, task.kwargs)),
            'Result': "None" if task.result is None else task.result.replace('\n', '<br>'),
            'Group': task.group,
            "Started by user": serverfile.started_at,
            "Added to queue": task.added,
            'Started': task.started,
            'Stopped': task.stopped,
            "Success": task.success,
            "Queue size": django_q.tasks.queue_size(),
            "Queue length": len(django_q.models.Task.objects.all()),
            "Queue tasks": pprint.pformat(django_q.models.Task.objects.all().order_by('-started')[:10]),
        }

        # if not task.success:
        #     key_value = {
        #         'Id': task.id,
        #         'Name': task.name,
        #         'Func': task.func,
        #         'Hook': task.hook,
        #         'Args': ", ".join(map(str, task.args)),
        #         'Kwargs': ", ".join(map(str, task.kwargs)),
        #         'Result': task.result.replace('\n', '<br>'),
        #         'Group': task.group,
        #         'Started': task.started,
        #         'Stopped': task.stopped,
        #         "Success": task.success,
        #     }

    if (len(msg) > 0) and ((task is None) or task.success):
        key_value = {"Error": msg}

    opath = Path(serverfile.outputdir)
    # outputdir_url = opath.exists()
    if opath.exists():
        key_value.update({
            "Files": "<br>".join(map(os.path.basename, glob.glob(str(opath / "*.*"))))
        })

        logpath = opath / "log.txt"
        if logpath.exists():
            with open(logpath) as f:
                lines = f.readlines()

            lines = [_set_loglevel_color(line) for line in lines]
            key_value.update({
                "Log": '<p class="text-monospace">' + "<br>".join(lines) + '</p>'
            })

    # if filename.exists():

    return render(request, 'microimprocessing/file_log.html',
                  {'serverfile': serverfile, 'df_html':None, "image_list":None, 'key_value': key_value,
                   'download_button': opath.exists()
                   })

def _set_loglevel_color(line):
    line = line.replace("DEBUG", '<b class="log-debug">DEBUG</b>')
    line = line.replace("ERROR", '<b class="log-error">ERROR</b>')
    line = line.replace("INFO", '<b class="log-info">INFO</b>')
    line = line.replace("TRACE", '<b class="log-trace">TRACE</b>')
    line = line.replace("WARNING", '<b class="log-warning">WARNING</b>')
    return line

def _preapare_xlsx_for_rendering(filename:Path, additional_keys=None):
    logger.debug(filename)
    df_html = None
    if filename.exists():
        import pandas as pd
        dfall = pd.read_excel(str(filename), sheet_name="Sheet1",
                              # index=False,
                              # index_col=0
                              #index_col=None
                              engine='openpyxl'

                              )
        key_candidate = ["Skeleton length", "Branch number", "Dead ends number",
                         "Area", "Area unit", "Lobulus Perimeter", # "Lobulus Equivalent Surface",
                         "Annotation Center X [mm]", "Annotation Center Y [mm]",
                         "Scan Segmentation Empty Area [mm^2]", "Scan Segmentation Septum Area [mm^2]",
                         "Scan Segmentation Sinusoidal Area [mm^2]","SNI area prediction", "SNI prediction CNN"
                         ]
        if additional_keys:
            key_candidate += additional_keys
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
    image_list = serverfile.bitmapimage_set.all()

    return render(request, 'microimprocessing/detail.html',
                  {'serverfile': serverfile, 'df_html':df_html, "image_list":image_list})


def common_spreadsheet(request):

    filename,url,_ = models.get_common_spreadsheet_file(request.user)
    # serverfile = get_object_or_404(ServerDataFileName, pk=filename_id)
    # filename = Path(serverfile.outputdir) / "data.xlsx"

    # import glob
    # image_list = glob.glob(str(Path(serverfile.outputdir) / "lobulus_*.png"))

    df_html = _preapare_xlsx_for_rendering(filename, additional_keys=["File Name"])
    image_list = []
    return render(request, 'microimprocessing/detail.html',
                  {
                      'serverfile': "Common Spreadsheet",
                      'df_html': df_html,
                      "image_list": image_list,
                      "spreadsheet_url": url,
                      "spreadsheet_url_tooltip": "Download the table"
                  }
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
            logger.debug(f"imagefile.name={dir(form)}")
            name = form.cleaned_data['imagefile']
            if name is None or name == '':
                return render(request, 'microimprocessing/model_form_upload.html', {
                    'form': form,
                    "headline": "Upload",
                    "button": "Upload",
                    "error_text": "Image File is mandatory"
                })

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
        'form': form,
        "headline": "Upload",
        "button": "Upload"
    })

def _show_hide_tag(request, tag_id):
    tag = get_object_or_404(Tag, pk=tag_id)
    if "hide_tags" in request.session:
        hide = request.session["hide_tags"]
    else:
        hide = []
        request.session["hide_tags"] = hide
    if "show_tags" in request.session:
        show = request.session["show_tags"]
    else:
        show = []
        request.session["show_tags"] = show
    # hide = request.session.get("hide_tags", [])
    # show = request.session.get("show_tags", [])
    logger.debug(f"show={show}")
    logger.debug(f"hide={hide}")
    return show, hide, tag

def show_tag(request, tag_id):
    show, hide, tag = _show_hide_tag(request, tag_id)
    if tag_id in hide:
        hide.remove(tag_id)
        request.session.modified = True
    if tag_id not in show:
        show.append(tag_id)
        request.session.modified = True

    return redirect('/microimprocessing/')

def hide_tag(request, tag_id):
    show, hide, tag = _show_hide_tag(request, tag_id)
    if tag_id in show:
        show.remove(tag_id)
        request.session.modified = True
    if tag_id not in hide:
        hide.append(tag_id)
        request.session.modified = True

    return redirect('/microimprocessing/')


def ignore_tag(request, tag_id, do_redirect=True):
    show, hide, tag = _show_hide_tag(request, tag_id)
    if tag_id in show:
        show.remove(tag_id)
    if tag_id in hide:
        hide.remove(tag_id)

    request.session.modified = True
    if do_redirect:
        return redirect('/microimprocessing/')


def create_tag(request, filename_id=None):
    if request.method == 'POST':
        form = TagForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data['name']
            objs = Tag.objects.filter(name=name)
            if len(objs) == 0:
                tag = form.save()
            else:
                tag = objs[0]

            tag.users.add(request.user)
            tag.save()
            if filename_id:
                _add_tag(request.user, filename_id, tag.id)
            return redirect('/microimprocessing/')
    else:
        form = TagForm

    return render(request, 'microimprocessing/model_form_upload.html', {
        'form': form,
        "headline": 'Create Tag',
        "button": "Create",
    })


def _add_tag(user, filename_id, tag_id):
    serverfile = get_object_or_404(ServerDataFileName, pk=filename_id)
    tag = get_object_or_404(Tag, pk=tag_id)
    tag.users.add(user)
    tag.files.add(serverfile)
    tag.save()


def add_tag(request, filename_id, tag_id):
    _add_tag(request.user, filename_id, tag_id)
    return redirect('/microimprocessing/')


def set_order_by(request, order_by):
    request.session["order_by"] = order_by
    request.session.modified = True
    return redirect('/microimprocessing/')

def remove_tag(request, filename_id, tag_id):
    serverfile = get_object_or_404(ServerDataFileName, pk=filename_id)
    tag = get_object_or_404(Tag, pk=tag_id)
    tag.files.remove(serverfile)
    tag.save()
    return redirect('/microimprocessing/')


def remove_tag_from_user(request, tag_id):
    tag = get_object_or_404(Tag, pk=tag_id)
    logger.debug(f"delete tag {tag}")
    ignore_tag(request,tag_id=tag_id, do_redirect=False)
    for file in tag.files.filter(owner=request.user):
        tag.files.remove(file)
    tag.users.remove(request.user)
    tag.save()
    return redirect('/microimprocessing/')


def run_processing(request, pk, parameters=None):
    logger.debug("run processing view")
    from django_q.tasks import async_task, result
    serverfile:ServerDataFileName = get_object_or_404(ServerDataFileName, pk=pk)

    serverfile.process_started = True
    serverfile.outputdir = get_output_dir()
    serverfile.started_at = datetime.now()
    serverfile.save()

    logger.debug(f"parameters={parameters}")
    tid = async_task(
        'microimprocessing.tasks.run_processing', serverfile, parameters,
                     # hook="microimprocessing.views.make_thumbnail"
        hook='microimprocessing.tasks.finish_processing',
    )
    serverfile.last_task_uuid = tid
    serverfile.save()

    return redirect('/microimprocessing/')




def add_example_data(request):
    logger.debug("add example data")
    all = ExampleData.objects.all()
    for sample_image in all:
        logger.debug("add data")
        sdf = sample_image.server_datafile
        if Path(sdf.imagefile.path).exists():
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
            tag = models.get_tag_by_name("Sample")
            _add_tag(user=request.user, filename_id=new_sdf.id, tag_id=tag.id)
            make_thumbnail(new_sdf)
            # new_sdf.save()
            logger.debug(f"newsdf.owner{new_sdf.owner}, new_sdf.imagefile={new_sdf.imagefile}")
        else:
            logger.warning(f"Example file '{sdf.imagefile.name}' not found. Skipping.")

    return redirect('/microimprocessing/')


def gdrive_import(request):
    from django_q.tasks import async_task
    logger.debug("gdrive import")
    async_task('microimprocessing.tasks.run_gdrive_import')
    # tasks.run_gdrive_import()
    return redirect('/microimprocessing/')


# TODO add scaffan parameter edit
# def default_scaffan_params(request):
#     mainapp.parameters_to_dict()

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


# import datetime
# from django.forms import formset_factory
# from myapp.forms import ArticleForm
# ArticleFormSet = formset_factory(ArticleForm, extra=2)
# formset = ArticleFormSet(initial=[
#     {'title': 'Django is now open source',
#      'pub_date': datetime.date.today(),}
# ])

def pre_run(request, filename_id):
    # return redirect('/microimprocessing/')
    serverfile = get_object_or_404(ServerDataFileName, pk=filename_id)

    # book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        # RenewBookForm(request.)

        form = ScaffanParameters(request.POST)

        # # Check if the form is valid:
        if form.is_valid():
            logger.debug("is valid")
            logger.debug(pprint.pformat(form.cleaned_data))
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            # book_instance.due_back = form.cleaned_data['renewal_date']
            # book_instance.save()
        #
        #     # redirect to a new URL:
        #     return HttpResponseRedirect(reverse('all-borrowed') )

            logger.debug("Redy to run")

            return run_processing(request, filename_id, form.cleaned_data)

            # return redirect('/microimprocessing/')

    # If this is a GET (or any other method) create the default form.
    else:
        # proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        # form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})
        form = ScaffanParameters()

    import scaffan.algorithm
    mainapp = scaffan.algorithm.Scaffan()
    parameters_as_cfg_string = mainapp.get_parameters_as_cfg_string()
    from django.forms import formset_factory
    # BookSet = formset_factory(RenewBookForm,
    #                           # extra=3
    #                           )
    # data = {
    # 'form-TOTAL_FORMS': '2',
    # 'form-INITIAL_FORMS': '0',
    # 'form-0-name': 'Test',
    # 'form-0-value': '1904-06-16',
    # 'form-0-value-label': 'osadfs',
    # 'form-1-name': 'Test',
    # 'form-1-value': '',  # <-- this date is missing but required
    # }
    # bforms = BookSet(data)

    from django import forms
    context = {
        'form': form,
        'button': "Run"
        # 'parameters': parameters_as_cfg_string,
        # 'fm' : bforms

        # 'book_instance': book_instance,
    }

    return render(request, 'microimprocessing/pre_run.html', context)
