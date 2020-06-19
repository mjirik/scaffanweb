from django.db import models
# import io3d
from datetime import datetime
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from . import scaffanweb_tools

User = get_user_model()
# Create your models here.

# pth = io3d.datasets.join_path(get_root=True)
from pathlib import Path
pth = Path("~/data/medical/orig/Scaffan-analysis").expanduser()

def get_output_dir():
    #
    import datetime
    import os.path as op
    # OUTPUT_DIRECTORY_PATH = "~/cellid_data"
    OUTPUT_DIRECTORY_PATH = settings.MEDIA_ROOT
    filename = op.join(op.expanduser(OUTPUT_DIRECTORY_PATH), datetime.datetime.now().strftime("%Y%m%d-%H%M%S.%f") + "_" + scaffanweb_tools.randomString(8))
    return filename

class ServerDatasetPath(models.Model):
    comment = models.CharField(max_length=200)
    server_dataset_path = models.FilePathField("Path to dataset on server", path=str(pth), allow_files=False, allow_folders=True)



class ServerDataFileName(models.Model):

    # server_dataset_path= models.ForeignKey(ServerDatasetPath, on_delete=models.CASCADE)
    # choice_text = models.CharField(max_length=200)
    processed = models.BooleanField(default=False)
    owner = models.ForeignKey(
        # settings.AUTH_USER_MODEL,
        User,
        on_delete=models.CASCADE, null=True
        # blank=True
    )
    # users = models.ManyToManyField(Publication)
    processed_in_version = models.CharField(max_length=200)
    # imagefile_path = models.FilePathField("File Path",path=str(pth), allow_files=True, allow_folders=False, recursive=True, blank=True)
    imagefile = models.FileField("Uploaded File", upload_to="documents/", blank=True, null=True)
    annotationfile = models.FileField("Annotation File", upload_to="documents/", blank=True, null=True)
    # thumbnail = models.CharField("Thumbnail File", max_length=255, blank=True)
    preview = models.ImageField(upload_to="cellimage/", blank=True)
    zip_file = models.ImageField(upload_to="cellimage/", blank=True)
    preview_pixelsize_mm = models.FloatField("Preview Pixelsize [mm]", blank=True, null=True)
    description = models.CharField(max_length=255, blank=True)
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
    #     return reverse('imviewer:image-detail', args=[str(self.id)])

