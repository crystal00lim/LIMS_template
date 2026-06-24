from django.urls import path
from . import views

app_name = 'freedberg'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
]