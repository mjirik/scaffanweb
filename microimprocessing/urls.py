from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'microimprocessing'
urlpatterns = [
    path('', views.index, name='index'),

    # ex: /polls/5/
    path('<int:filename_id>/', views.detail, name='detail'),
    path('upload/', views.model_form_upload, name='model_form_upload'),
    path('<int:pk>/run_processing/', views.run_processing, name='run_processing'),
    path('logout/', views.logout_view, name='logout_view'),
    path('add_example_data/', views.add_example_data, name='add_example_data'),
    path('<int:filename_id>/delete_file/', views.delete_file, name='delete_file'),
]