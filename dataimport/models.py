from django.db import models
# import io3d

# Create your models here.

# pth = io3d.datasets.join_path(get_root=True)
from pathlib import Path
pth = Path("~/data/medical/orig/Scaffan-analysis").expanduser()


class ServerDatasetPath(models.Model):
    comment = models.CharField(max_length=200)
    server_dataset_path = models.FilePathField("Path to dataset on server", path=str(pth), allow_files=False, allow_folders=True)


class ServerDataFileName(models.Model):
    server_dataset_path= models.ForeignKey(ServerDatasetPath, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    processed = models.BooleanField()
    processed_in_version = models.CharField(max_length=200)
    file_path = models.FilePathField("File Path on server",path=str(pth), allow_files=True, allow_folders=False, recursive=True)
    # votes = models.IntegerField(default=0)