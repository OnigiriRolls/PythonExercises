from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("home/", views.home_view, name="home"),
    path("logout/", views.logout_view, name="logout"),
    path("get-temperatures/", views.get_temperatures_view, name="get_temperatures"),
]
