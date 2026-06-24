from django.urls import path
from . import views

app_name = 'doxypep'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
]