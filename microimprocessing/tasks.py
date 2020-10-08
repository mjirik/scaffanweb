from loguru import logger
from pathlib import Path
import numpy as np
from .models import ServerDataFileName, LobuleCoordinates, ExampleData
from .models import get_output_dir, get_tag_by_name
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

# report generator
def create_html_report(user):
    html_report = 'We had a great quarter!'
    logger.debug(html_report)
    return html_report


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

def run_processing(serverfile:ServerDataFileName):
    import scaffan
    import scaffan.algorithm
    import scaffan.image
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
    mainapp = scaffan.algorithm.Scaffan()
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
    mainapp.run_lobuluses(seeds_mm=centers_mm)

    serverfile.process_started = False
    serverfile.save()

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/drive.readonly', 'https://www.googleapis.com/auth/drive.file']

def _iterate_gdrive_import_files(
        credentials_json='credentials_mjirik_gapps.json',
        token_pickle='token.pickle',
        drive_id="0AHtTDixl96VzUk9PVA",  # my Zeiss Scann ID
        dir_id='1OsKfZlp_s6RPHXXei8LsZunTNjPsBwMb',
        file_extension=None
):
    """

    :param credentials_json: path to credentials in json format. It can be obtained by activating Google API
    :param token_pickle: path to token in pickle. It can be created automatically interactively by first run.
    :param drive_id: Google Drive ID
    :param dir_id: Google Directory ID
    :return:
    """
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
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)
    q = f"'{dir_id}' in parents"
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
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])


    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))

        file_id = item["id"]
        name = item['name']
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
        file_extension=gdriveimport.extension
    ):
        if name not in known_filenames:
            new_sdf = ServerDataFileName(
                owner=user,
                # imagefile=sdf.,
                # preview=sdf.preview,
                description="Auto Import",
                # preview=ContentFile(sdf.preview.read()),
            )
            logger.debug(f"new_sdf name={name}, new_sdf.imagefile={new_sdf.imagefile}")
            new_sdf.imagefile.save(name, ContentFile(fh.read()), save=True)
            new_sdf.save()
            tag = get_tag_by_name("Imported")
            views._add_tag(user=user, filename_id=new_sdf.id, tag_id=tag.id)
            make_thumbnail(new_sdf)


def run_gdrive_import():
    for gdriveimport in models.GDriveImport.objects.all():
        for user in gdriveimport.user.all():
            _run_gdrive_import_for_user(gdriveimport, user)


# Use the schedule wrapper
from django_q.tasks import schedule

schedule(
    'tasks.run_gdrive_import',
         # hook='hooks.print_result',
         schedule_type='H',
        name="Google Drive Import"
)