import pandas
from loguru import logger
import loguru
from pathlib import Path
import numpy as np
from .models import ServerDataFileName, LobuleCoordinates, ExampleData
from .models import get_output_dir, get_tag_by_name
from .data_tools import google_spreadsheet_append
import os.path as op
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload
import io
import pickle
from django.core.files.base import ContentFile
from scaffanweb import settings
from microimprocessing import scaffanweb_tools, models, views
import glob
import sys
from typing import Optional
import django_q
from oauth2client.service_account import ServiceAccountCredentials

pth_to_scaffan = Path(__file__).parent.parent.parent / "scaffan"
logger.debug(pth_to_scaffan)
logger.debug(pth_to_scaffan.exists())
if pth_to_scaffan.exists():
    sys.path.insert(0, str(pth_to_scaffan))

from .scaffanweb_tools import resize_image, crop_square

# report generator
def create_html_report(user):
    html_report = 'We had a great quarter!'
    logger.debug(html_report)
    return html_report


def get_zip_fn(serverfile:ServerDataFileName):
    logger.trace(f"serverfile.imagefile={serverfile.imagefile.name}")
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

def force_update_task():
    logger.debug("Force update")

    logger.debug("updating last tasks...")
    update_last_tasks()
    # prepare images
    latest_filenames = ServerDataFileName.objects.all()


    logger.debug("updating generated images...")
    for serverfile in latest_filenames:
        logger.debug(serverfile)
        delete_generated_images(serverfile)
        add_generated_images(serverfile)
        try:
            make_thumbnail(serverfile)
        except Exception as e:
            logger.warning(e)

    logger.debug("updating ZIP files...")
    # finish run by creating zip file if xlsx file exists
    for serverfile in latest_filenames:
        if (Path(serverfile.outputdir) / "data.xlsx").exists():
            logger.debug(f"output exists: {serverfile.outputdir}")
            zip_fn = get_zip_fn(serverfile)
            if zip_fn:
                if not Path(zip_fn).exists():
                    make_zip(serverfile)
                    serverfile.process_started = False
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
    ptht = str(Path(settings.MEDIA_ROOT) / (nm + ".thumbnail.jpg"))
    # pth = serverfile.outputdir + nm + ".preview.jpg"

    # pth = serverfile.imagefile.path + ".thumbnail.jpg"
    logger.debug("")
    logger.debug(f"preview={pth}")
    logger.debug(f"thumbnail={ptht}")
    pth_rel = op.relpath(pth, settings.MEDIA_ROOT)
    ptht_rel = op.relpath(ptht, settings.MEDIA_ROOT)
    logger.debug(pth_rel)
    serverfile.preview = pth_rel
    serverfile.thumbnail = ptht_rel
    serverfile.preview_pixelsize_mm = pxsz_mm
    import skimage.io
    logger.debug(f"img max: {np.max(img)}, img.dtype={img.dtype}")
    if img.dtype != np.uint8:
        img = (img*255).astype(np.uint8)
    skimage.io.imsave(pth, img[:,:,:3])
    imgt = resize_image(img[:,:,:3], height=300)
    imgt = crop_square(imgt)

    skimage.io.imsave(pth, img[:,:,:3])
    skimage.io.imsave(ptht, imgt[:,:,:3])

    serverfile.save()


def update_last_tasks():
    for serverfile in models.ServerDataFileName.objects.all():
        _update_last_task(serverfile)


def _update_last_task(serverfile:ServerDataFileName):
    tasks_of_file = [tsk for tsk in django_q.models.Task.objects.all().order_by('-started') if
                         ((len(tsk.args) > 0) and (tsk.args[0] == serverfile))]

    serverfile.last_task_uuid = tasks_of_file[0].id if len(tasks_of_file) > 0 else None

    serverfile.save()


def run_processing(serverfile:ServerDataFileName, parameters:Optional):
    import scaffan
    import scaffan.algorithm
    import scaffan.image
    log_format = loguru._defaults.LOGURU_FORMAT
    logger_id = logger.add(
        str(Path(serverfile.outputdir) / "log.txt"),
        format=log_format,
        level='DEBUG',
        rotation="1 week",
        backtrace=True,
        diagnose=True
    )
    delete_generated_images(serverfile) # remove images from database and the output directory
    coords = LobuleCoordinates.objects.filter(server_datafile=serverfile)

    centers_mm = [[coord.x_mm, coord.y_mm] for coord in coords]

    logger.debug(coords)
    # serverfile.outputdir = get_output_dir()
    # serverfile.process_started = True
    serverfile.save()

    # cli_params = [
    #     settings.CONDA_EXECUTABLE, "run", "-n", "scaffanweb", "python", "-m", "scaffan", "-lf",
    #     str(Path(serverfile.outputdir) / 'scaffan.log'), "nogui",
    #     "-i", str(serverfile.imagefile.path),
    #     "-o", str(serverfile.outputdir),
    # ]
    # for coord in coords:
    #     cli_params.append("--seeds_mm")
    #     cli_params.append(str(coord.x_mm))
    #     cli_params.append(str(coord.y_mm))
    #
    # logger.debug(f"adding task to queue CLI params: {' '.join(cli_params)}")

    logger.debug("Scaffan processing init")
    logger.debug(f"image path: {serverfile.imagefile.path}")
    mainapp:scaffan.algorithm.Scaffan = scaffan.algorithm.Scaffan()
    logger.debug(f"parameters={parameters}")
    if parameters:
        for key, value  in parameters.items():
            mainapp.set_parameter(key, value)
    mainapp.set_input_file(serverfile.imagefile.path)
    mainapp.set_output_dir(serverfile.outputdir)
    fn,_,_ = models.get_common_spreadsheet_file(serverfile.owner)
    mainapp.set_common_spreadsheet_file(str(fn).replace("\\", "/"))
    # settings.SECRET_KEY
    logger.debug("Scaffan processing run")
    if len(centers_mm) > 0:
        mainapp.set_parameter("Input;Lobulus Selection Method", "Manual")
    else:
        mainapp.set_parameter("Input;Lobulus Selection Method", "Auto")

    mainapp.report.set_persistent_cols({"username": serverfile.owner.username})
    mainapp.run_lobuluses(seeds_mm=centers_mm)
    if "SNI area prediction" in mainapp.report.df:
        serverfile.score = _clamp(mainapp.report.df["SNI area prediction"].mean() * 0.5, 0., 1.)
    if "Skeleton length" in mainapp.report.df:
        serverfile.score_skeleton_length = mainapp.report.df["Skeleton length"].mean()
    if "Branch number" in mainapp.report.df:
        serverfile.score_branch_number = mainapp.report.df["Branch number"].mean()
    if "Dead ends number" in mainapp.report.df:
        serverfile.score_dead_ends_number = mainapp.report.df["Dead ends number"].mean()
    if "Area" in mainapp.report.df:
        serverfile.score_area = mainapp.report.df["Area"].mean()

    logger.debug("Appending to Google Spreadsheet")
    _add_rows_to_spreadsheet(mainapp.report.df)

    add_generated_images(serverfile) # add generated images to database

    serverfile.processed_in_version = scaffan.__version__
    serverfile.process_started = False
    serverfile.last_error_message = ''
    if serverfile.zip_file and Path(serverfile.zip_file.path).exists():
        serverfile.zip_file.delete()

    views.make_zip(serverfile)
    serverfile.save()
    logger.remove(logger_id)

def _add_rows_to_spreadsheet(df:pandas.DataFrame):
    """
    Append rows to spreadsheet
    """

    creds_file = Path(settings.CREDS_JSON_FILE)  # 'piglegsurgery-1987db83b363.json'
    if not creds_file.exists():
        logger.error(f"Credetials file does not exist. Expected path: {creds_file}")
        return
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)

    google_spreadsheet_append(
        title="ScaffAn Stats",
        creds=creds,
        data=df
    )

def finish_processing(task):
    logger.debug("run processing finish")
    serverfile: ServerDataFileName = task.args[0]
    serverfile.process_started = False
    serverfile.save()

    # absolute uri is http://127.0.0.1:8000/. We have to remove last '/' because the url already contains it.
    # absolute_uri = task.args[1][:-1]
    # logger.debug(dir(task))
    # this does not work

    if task.args and len(task.args) > 0:
        serverfile = task.args[0]

    if task.success:
        pass
    else:
        pass


def add_generated_images(serverfile:ServerDataFileName):
    # serverfile.bitmap_image_set.all().delete()
    od = Path(serverfile.outputdir)
    logger.debug(od)
    lst = glob.glob(str(od / "slice_raster.png"))
    # lst.extend(glob.glob(str(od / "slice_label.png")))
    lst.extend(sorted(glob.glob(str(od / "preview_with_annotations.png"))))
    # lst.extend(glob.glob(str(od / "sinusoidal_tissue_local_centers.png")))
    lst.extend(sorted(glob.glob(str(od / "lobulus_[0-9]*.png"))))
    lst.extend(sorted(glob.glob(str(od / "skeleton_lowres_[0-9]*.png"))))
    logger.debug(lst)

    for fn in lst:
        pth_rel = op.relpath(fn, settings.MEDIA_ROOT)
        bi = models.BitmapImage(server_datafile=serverfile, bitmap_image=pth_rel)
        bi.save()


def delete_generated_images(serverfile:ServerDataFileName):
    serverfile.bitmapimage_set.all().delete()


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/drive.readonly', 'https://www.googleapis.com/auth/drive.file']


def _iterate_gdrive_import_files(
        credentials_json='credentials_mjirik_gapps.json',
        token_pickle='token.pickle',
        drive_id="0AHtTDixl96VzUk9PVA",  # my Zeiss Scann ID
        dir_id='1OsKfZlp_s6RPHXXei8LsZunTNjPsBwMb',
        file_extension=None,
        ignored_filenames=None
):
    """

    :param credentials_json: path to credentials in json format. It can be obtained by activating Google API
    :param token_pickle: path to token in pickle. It can be created automatically interactively by first run.
    :param drive_id: Google Drive ID
    :param dir_id: Google Directory ID
    :return:
    """
    if not ignored_filenames:
        ignored_filenames = []
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(token_pickle):
        with open(token_pickle, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_json, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_pickle, 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)
    q = f"'{dir_id}' in parents and trashed = false"
    if file_extension:
        q += f" and fileExtension = '{file_extension}'"
    # Call the Drive v3 API
    results = service.files().list(
        driveId=drive_id,
        # q="name = '11_2019_11_13__-7.czi'",
        # q="mimeType = 'application/vnd.google-apps.folder'", # list all directories
        # q="'1pStkl9_vEQJHTAc0OIbP4X39GmcBhVBJ' in parents", # all files in Moulisova-Jena
        # q="'1OsKfZlp_s6RPHXXei8LsZunTNjPsBwMb' in parents", # all files in scaffan_import
        q=q, # all files in scaffan_import

        includeItemsFromAllDrives=True,
        supportsAllDrives=True,
        corpora="drive",
        pageSize=1000,
        fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        logger.debug('No files found.')
    else:
        logger.debug('Files:')
        for item in items:
            logger.debug(u'{0} ({1})'.format(item['name'], item['id']))

            file_id = item["id"]
            name = item['name']
            if name not in ignored_filenames:
                drive_service = service
                request = drive_service.files().get_media(fileId=file_id)
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    logger.debug("Download %d%%." % int(status.progress() * 100))
                yield fh, name


def _run_gdrive_import_for_user(gdriveimport:models.GDriveImport, user:models.User):
    """
    Import all available data for
    :param gdriveimport:
    :param user:
    :return:
    """

    known_filenames = [
        fn.name for fn in map(
            Path,
            models.ServerDataFileName.objects.filter(owner=user).values_list("imagefile", flat=True).distinct()
        )
    ]
    for fh, name in _iterate_gdrive_import_files(
        credentials_json=gdriveimport.credentials,
        token_pickle=gdriveimport.token,
        drive_id=gdriveimport.gdrive_id,
        dir_id=gdriveimport.gdir_id,
        file_extension=gdriveimport.extension,
        ignored_filenames=known_filenames
    ):
        new_sdf = ServerDataFileName(
            owner=user,
            # imagefile=sdf.,
            # preview=sdf.preview,
            description="Auto Import",
            # preview=ContentFile(sdf.preview.read()),
        )
        logger.debug(f"new_sdf user= {user} name={name}, new_sdf.imagefile={new_sdf.imagefile}")
        path_full = models.upload_to_unqiue_folder(new_sdf, name)
        logger.debug(f"full path={path_full}")

        ppath_full = Path(path_full)
        ppath_full.parent.mkdir(parents=True, exist_ok=True)

        with io.open(path_full, 'wb') as f:
            fh.seek(0)
            f.write(fh.read())
        # import pdb
        # pdb.set_trace()
        new_sdf.imagefile = path_full

        # new_sdf.imagefile.save(name, ContentFile(fh.read()), save=True)
        new_sdf.save()
        tag = get_tag_by_name("Imported")
        views._add_tag(user=user, filename_id=new_sdf.id, tag_id=tag.id)
        make_thumbnail(new_sdf)


def run_gdrive_import():
    for gdriveimport in models.GDriveImport.objects.all():
        for user in gdriveimport.user.all():
            logger.debug(f"gimport for user={user}")
            _run_gdrive_import_for_user(gdriveimport, user)

def _clamp(n, minn, maxn):
    return max(min(maxn, n), minn)
# Use the schedule wrapper
# from django_q.tasks import schedule
#
# schedule(
#     'tasks.run_gdrive_import',
#          # hook='hooks.print_result',
#          schedule_type='H',
#         name="Google Drive Import"
# )
