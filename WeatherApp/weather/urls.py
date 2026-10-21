from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    path("", views.main_page_view, name="main_page_view"),
    path("login/", views.login_user, name="login"),
    path("register/", views.register_view, name="register_view"),
    path("register_user/", views.register, name="register_user"),
    path("home/", views.home_view, name="home"),
    path("logout/", views.logout_view, name="logout"),
    path("get-temperatures/", api_views.get_temperatures_view, name="get_temperatures"),
    path("get-average/", api_views.get_average_view, name="get_average"),
]
