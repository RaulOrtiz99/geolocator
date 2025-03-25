from django.urls import path
from geolocatorapp import views

urlpatterns = [
    path('', views.upload_csv, name='upload_csv'),
]