from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('main/<student>/<interest>/', views.main, name='main'),
]