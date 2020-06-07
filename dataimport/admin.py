from django.contrib import admin

# Register your models here.

from django.contrib import admin

from .models import ServerDataFileName, ServerDatasetPath

admin.site.register(ServerDataFileName)
admin.site.register(ServerDatasetPath)
