from django.db import models
# import io3d
from datetime import datetime
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from loguru import logger
import os.path as op
from . import scaffanweb_tools
from django.contrib.auth.models import User

User = get_user_model()
# Create your models here.

# pth = io3d.datasets.join_path(get_root=True)
from pathlib import Path
pth = Path("~/data/medical/orig/Scaffan-analysis").expanduser()

def get_output_dir():
    #
    # import datetime
    OUTPUT_DIRECTORY_PATH = settings.MEDIA_ROOT
    # datetimestr = datetime.datetime.now().strftime("%Y%m%d-%H%M%S.%f")
    datetimestr = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = op.join(
        op.expanduser(OUTPUT_DIRECTORY_PATH),
        "SA_" + datetimestr + "_" + scaffanweb_tools.randomString(12),
        "SA_" + datetimestr
    )
    return filename

def get_default_user_hash():
    return scaffanweb_tools.randomString(12)

def upload_to_unqiue_folder(instance, filename):
    """
    Uploads a file to an unique generated Path to keep the original filename
    """
    logger.debug("upload_to_unique_folder")
    logger.debug(instance)
    logger.debug(filename)
    logger.debug(instance.uploaded_at)
    hash = scaffanweb_tools.generate_sha1(instance.uploaded_at, "_")

    instance_filename = Path(instance.imagefile.path).stem

    datetimestr = datetime.now().strftime("%Y%m%d-%H%M%S")

    return op.join(
        settings.UPLOAD_PATH,
        datetimestr + "_" + instance_filename + "_" + hash,
        filename
    )
    # return 's%()%(path)s%(hash_path)s%(filename)s' % {'path': settings.UPLOAD_PATH,
    #                                            'hash_path': scaffanweb_tools.randomString(12),
    #                                            'filename': filename}


class ServerDatasetPath(models.Model):
    comment = models.CharField(max_length=200)
    server_dataset_path = models.FilePathField("Path to dataset on server", path=str(pth), allow_files=False, allow_folders=True)


class ServerDataFileName(models.Model):

    # server_dataset_path= models.ForeignKey(ServerDatasetPath, on_delete=models.CASCADE)
    # choice_text = models.CharField(max_length=200)
    processed = models.BooleanField(default=False)
    process_started = models.BooleanField(default=False)
    owner = models.ForeignKey(
        # settings.AUTH_USER_MODEL,
        User,
        on_delete=models.CASCADE, null=True
        # blank=True
    )
    # users = models.ManyToManyField(Publication)
    processed_in_version = models.CharField(max_length=200)
    # imagefile_path = models.FilePathField("File Path",path=str(pth), allow_files=True, allow_folders=False, recursive=True, blank=True)
    hash = scaffanweb_tools.randomString(12)
    imagefile = models.FileField("Uploaded File", upload_to=upload_to_unqiue_folder, blank=True, null=True, max_length=500)
    annotationfile = models.FileField("Annotation File", upload_to=upload_to_unqiue_folder, blank=True, null=True, max_length=500)
    # thumbnail = models.CharField("Thumbnail File", max_length=255, blank=True)
    preview = models.ImageField(upload_to="cellimage/", blank=True)
    zip_file = models.ImageField(upload_to="cellimage/", blank=True, null=True)
    preview_pixelsize_mm = models.FloatField("Preview Pixelsize [mm]", blank=True, null=True)
    description = models.CharField(max_length=255, blank=True)
    # orig_filename = models.CharField(max_length=255, blank=True)
    # multicell_dapi = models.FileField(upload_to='documents/')
    # multicell_fitc = models.FileField(upload_to='documents/')
    # singlecell_dapi = models.FileField(upload_to='documents/')
    # singlecell_fitc = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(
        # auto_now_add=True,
        # blank=True) #,
        default=datetime.now
    )
    outputdir = models.CharField(max_length=255, blank=True, default=get_output_dir)
    # image_preview = models.ImageField(upload_to="image_preview/", blank=True)
    # votes = models.IntegerField(default=0)

    def __str__(self):
        if self.imagefile:
            return f"{Path(self.imagefile.path).name} {self.description}"
        else:
            return self.description


class LobuleCoordinates(models.Model):
    server_datafile = models.ForeignKey(ServerDataFileName, on_delete=models.CASCADE)
    x_mm = models.FloatField("X [mm]")
    y_mm = models.FloatField("Y [mm]")

    # def get_absolute_url(self):
    #     """
    #     Returns the url to access a particular book instance.
    #     """
    #     print("models get_absolute_url()")
    #     print(self.id)
    #     return reverse('imviewer:image-set_lobules_seeds', args=[str(self.id)])


class ExampleData(models.Model):
    server_datafile = models.ForeignKey(ServerDataFileName, on_delete=models.CASCADE)

class Tag(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True
    )
    name = models.CharField(max_length=50)
    files = models.ManyToManyField(ServerDataFileName)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # bio = models.TextField(max_length=500, blank=True)
    # location = models.CharField(max_length=30, blank=True)
    # birth_date = models.DateField(null=True, blank=True)
    hash = models.CharField(max_length=50, default=get_default_user_hash)
    automatic_import = models.BooleanField(default=False)
