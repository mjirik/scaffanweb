from django.contrib import admin

# Register your models here.

from django.contrib import admin

from .models import ServerDataFileName, ServerDatasetPath, LobuleCoordinates, ExampleData

admin.site.register(ServerDataFileName)
admin.site.register(ServerDatasetPath)
admin.site.register(LobuleCoordinates)
admin.site.register(ExampleData)
