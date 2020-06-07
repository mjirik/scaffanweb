from django.urls import path

from . import views

app_name = 'dataimport'
urlpatterns = [
    path('', views.index, name='index'),

    # ex: /polls/5/
    path('<int:filename_id>/', views.detail, name='detail'),
    path('upload/', views.model_form_upload, name='model_form_upload'),
]