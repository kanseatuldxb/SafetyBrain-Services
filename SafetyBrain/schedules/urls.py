from django.urls import path
from . import views

urlpatterns = [
    path('schedules/', views.Schedule.as_view(), name='login'),
]