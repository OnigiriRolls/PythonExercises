import os
import requests

from django.conf import settings
from decimal import Decimal
from django.db.models import Avg, Count
from .models import WeatherReading, TemperatureAverage


def fetch_and_save_weather(latitude=51.2, longitude=12.5):
    api_key = os.environ.get("WEATHERBIT_API_KEY")
    if not api_key:
        raise ValueError("Weatherbit API key is not configured.")

    response = requests.get(
        settings.WEATHERBIT_API_URL,
        params={
            "lat": latitude,
            "lon": longitude,
            "key": api_key,
        },
        timeout=settings.WEATHERBIT_API_TIMEOUT,
    )
    response.raise_for_status()

    result = response.json()
    weather_data = []
    for weather in result.get("data", []):
        reading = WeatherReading.objects.create(
            city_name=weather.get("city_name") or "",
            country_code=weather.get("country_code") or "",
            latitude=Decimal(str(weather["lat"])),
            longitude=Decimal(str(weather["lon"])),
            temperature=Decimal(str(weather["temp"])),
            feels_like_temperature=Decimal(str(weather["app_temp"])),
        )

        weather_data.append(
            {
                "city_name": reading.city_name,
                "country_code": reading.country_code,
                "lat": reading.latitude,
                "lon": reading.longitude,
                "temp": reading.temperature,
                "app_temp": reading.feels_like_temperature,
            }
        )

    return weather_data


def calculate_and_save_average(latitude=51.2, longitude=12.5):
    result = WeatherReading.objects.aggregate(
        average=Avg("temperature"),
        count=Count("id"),
    )

    average = result["average"]
    count = result["count"]

    if average is not None:
        average = round(average, 2)
        TemperatureAverage.objects.create(
            latitude=Decimal(str(latitude)),
            longitude=Decimal(str(longitude)),
            average_temperature=average,
            count=count,
        )

    return {
        "average": average,
        "count": count,
    }
