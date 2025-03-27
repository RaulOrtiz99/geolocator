from django.urls import path
from geolocatorapp import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('', views.upload_csv, name='upload_csv'),
    path('get_processing_status/', views.get_processing_status, name='get_processing_status'),
]

urlpatterns += staticfiles_urlpatterns()