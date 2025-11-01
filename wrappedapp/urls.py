from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login, name="login"),
    path("callback/", views.callback, name="callback"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("artists", views.artists, name="artists"),
    path("genres", views.genres, name="genres"),
    path("logout/", views.logout, name="logout")
]