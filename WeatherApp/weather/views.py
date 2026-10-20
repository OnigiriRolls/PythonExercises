import requests
import os

from decimal import Decimal
from .models import WeatherReading
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.db.models import Avg, Count


def login_view(request):
    error = None

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        error = "Invalid username or password."

    return render(request, "login.html", {"error": error})


def register_view(request):
    error = None

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not username or not password or not confirm_password:
            error = "All fields are required."

        elif password != confirm_password:
            error = "Passwords do not match."

        elif User.objects.filter(username=username).exists():
            error = "This username is already taken."

        else:
            User.objects.create_user(username=username, password=password)
            return redirect("login")

    return render(request, "register.html", {"error": error})


@login_required
def home_view(request):
    context = {"username": request.user.username}
    return render(request, "home.html", context)


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def get_temperatures_view(request):
    weather_data = None
    api_error = None

    if request.method == "POST":
        api_key = os.environ.get("WEATHERBIT_API_KEY")

        if not api_key:
            api_error = "Weatherbit API key is not configured."
        else:
            try:
                response = requests.get(
                    "https://api.weatherbit.io/v2.0/current",
                    params={
                        "lat": 51.2,
                        "lon": 12.5,
                        "key": api_key,
                    },
                    timeout=10,
                )

                response.raise_for_status()
                result = response.json()

                if result.get("data"):
                    weather_data = []

                    for weather in result["data"]:
                        WeatherReading.objects.create(
                            city_name=weather.get("city_name") or "",
                            country_code=weather.get("country_code") or "",
                            latitude=Decimal(str(weather["lat"])),
                            longitude=Decimal(str(weather["lon"])),
                            temperature=Decimal(str(weather["temp"])),
                            feels_like_temperature=Decimal(str(weather["app_temp"])),
                        )

                        weather_data.append(
                            {
                                "city_name": weather.get("city_name"),
                                "country_code": weather.get("country_code"),
                                "lat": weather.get("lat"),
                                "lon": weather.get("lon"),
                                "temp": weather.get("temp"),
                                "app_temp": weather.get("app_temp"),
                            }
                        )
                else:
                    api_error = "No weather data was returned."

            except requests.RequestException:
                api_error = "Could not retrieve weather data. Please try again."
            except ValueError:
                api_error = "The API returned an invalid JSON response."

    return render(
        request,
        "home.html",
        {
            "username": request.user.username,
            "weather_data": weather_data,
            "api_error": api_error,
        },
    )


@login_required
def get_average_view(request):
    result = WeatherReading.objects.aggregate(
        average=Avg("temperature"),
        count=Count("id"),
    )

    average = result["average"]
    count = result["count"]

    if average is not None:
        average = round(average, 2)

    readings = WeatherReading.objects.order_by("-created_at")

    weather_data = [
        {
            "city_name": reading.city_name,
            "country_code": reading.country_code,
            "lat": reading.latitude,
            "lon": reading.longitude,
            "temp": reading.temperature,
            "app_temp": reading.feels_like_temperature,
        }
        for reading in readings
    ]

    return render(
        request,
        "home.html",
        {
            "username": request.user.username,
            "weather_data": weather_data,
            "average": average,
            "count": count,
        },
    )
