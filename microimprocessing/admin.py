from django.contrib import admin

# Register your models here.

from django.contrib import admin

from .models import ServerDataFileName, ServerDatasetPath, LobuleCoordinates

admin.site.register(ServerDataFileName)
admin.site.register(ServerDatasetPath)
admin.site.register(LobuleCoordinates)
