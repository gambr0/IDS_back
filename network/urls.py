from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('start/', views.start),
    path('stop/', views.stop),
]
