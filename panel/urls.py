from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('get_network_data/', views.get_network_data),
]
