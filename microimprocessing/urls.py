from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'microimprocessing'
urlpatterns = [
    path('', views.index, name='index'),

    # ex: /polls/5/
    path('<int:filename_id>/', views.set_lobules_seeds, name='set_lobules_seeds'),
    path('<int:filename_id>/detail', views.detail, name='detail'),
    path('common_spreadsheet', views.common_spreadsheet, name='common_spreadsheet'),
    path('upload/', views.model_form_upload, name='model_form_upload'),
    path('create_report/', views.create_report, name='create_report'),
    path('<int:pk>/run_processing/', views.run_processing, name='run_processing'),
    path('logout/', views.logout_view, name='logout_view'),
    path('add_example_data/', views.add_example_data, name='add_example_data'),
    path('<int:filename_id>/delete_file/', views.delete_file, name='delete_file'),
]