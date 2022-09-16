from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('profile/', views.Profile.as_view(), name='profile'),
    path('rules/', views.Rules.as_view(), name='rules'),
    path('staffs/', views.Persons.as_view(), name='staffs'),
    path('devices/', views.Devices.as_view(), name='devices'),
    path('events/', views.Event.as_view(), name='events'),
    path('healthscans/', views.HScans.as_view(), name='helthscans'),
    path('safetyscans/', views.SScans.as_view(), name='safetyscans'),
]