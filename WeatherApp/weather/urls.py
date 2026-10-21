from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    path("", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("home/", views.home_view, name="home"),
    path("logout/", views.logout_view, name="logout"),
    path("get-temperatures/", api_views.get_temperatures_view, name="get_temperatures"),
    path("get-average/", api_views.get_average_view, name="get_average"),
]
