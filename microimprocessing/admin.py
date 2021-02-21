from django.contrib import admin

# Register your models here.

from django.contrib import admin

from .models import (
    ServerDataFileName,
    ServerDatasetPath,
    LobuleCoordinates,
    ExampleData,
    Tag,
    Profile,
    GDriveImport,
    BitmapImage
)
import django_q.models as qmodels

admin.site.register(ServerDataFileName)
admin.site.register(ServerDatasetPath)
admin.site.register(LobuleCoordinates)
admin.site.register(ExampleData)
admin.site.register(Tag)
admin.site.register(Profile)
admin.site.register(GDriveImport)
admin.site.register(BitmapImage)

# admin.site.register(qmodels.Schedule)
