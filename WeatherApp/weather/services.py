import os
import re
import requests

from decimal import Decimal, InvalidOperation
from django.conf import settings
from django.db.models import Avg, Count
from .models import Location, WeatherReading, TemperatureAverage


def validate_location_input(city="", latitude="", longitude=""):
    city = city.strip()
    latitude = latitude.strip()
    longitude = longitude.strip()

    if not latitude and not longitude:
        if not city:
            raise ValueError("Enter a city or both latitude and longitude.")

        return {
            "city": city,
            "latitude": None,
            "longitude": None,
        }

    if not latitude or not longitude:
        raise ValueError("Enter both latitude and longitude.")

    decimal_pattern = re.compile(r"^-?\d+(\.\d{1,2})?$")
    if not decimal_pattern.fullmatch(latitude) or not decimal_pattern.fullmatch(
        longitude
    ):
        raise ValueError("Coordinates can have at most 2 decimal places.")

    try:
        lat = Decimal(latitude)
        lon = Decimal(longitude)
    except InvalidOperation:
        raise ValueError("Coordinates must be valid numbers.")

    if not lat.is_finite() or not lon.is_finite():
        raise ValueError("Coordinates must be finite numbers.")

    if not Decimal("-90") <= lat <= Decimal("90"):
        raise ValueError("Latitude must be between -90 and 90.")

    if not Decimal("-180") <= lon <= Decimal("180"):
        raise ValueError("Longitude must be between -180 and 180.")

    return {
        "city": city or None,
        "latitude": lat,
        "longitude": lon,
    }


def fetch_weather_data(city=None, latitude=None, longitude=None):
    api_key = os.environ.get("WEATHERBIT_API_KEY")
    if not api_key:
        raise ValueError("Weatherbit API key is not configured.")

    params = {"key": api_key}
    if latitude is not None and longitude is not None:
        params["lat"] = latitude
        params["lon"] = longitude
    elif city:
        params["city"] = city
    else:
        raise ValueError("Enter a city or both latitude and longitude.")

    response = requests.get(
        settings.WEATHERBIT_API_URL,
        params=params,
        timeout=settings.WEATHERBIT_API_TIMEOUT,
    )
    response.raise_for_status()
    return response.json().get("data", [])


def get_or_create_location(city_name, country_code, latitude, longitude):
    city_name = " ".join(city_name.split())
    normalized_city = city_name.casefold()
    country_code = country_code.strip().upper()

    location, _ = Location.objects.get_or_create(
        city_name_normalized=normalized_city,
        country_code=country_code,
        defaults={
            "city_name": city_name,
            "latitude": Decimal(str(latitude)),
            "longitude": Decimal(str(longitude)),
        },
    )
    return location


def resolve_location(city=None, latitude=None, longitude=None):
    weather_data = fetch_weather_data(
        city=city,
        latitude=latitude,
        longitude=longitude,
    )
    if not weather_data:
        raise ValueError("Weatherbit did not find this location.")

    weather = weather_data[0]
    city_name = (weather.get("city_name") or "").strip()
    country_code = (weather.get("country_code") or "").strip().upper()
    if not city_name or not country_code:
        raise ValueError("Could not identify the requested location.")

    return get_or_create_location(
        city_name=city_name,
        country_code=country_code,
        latitude=weather["lat"],
        longitude=weather["lon"],
    )


def fetch_and_save_weather(user, city=None, latitude=None, longitude=None):
    location_input = validate_location_input(
        city,
        latitude,
        longitude,
    )
    weather_data = fetch_weather_data(**location_input)

    saved_weather = []
    for weather in weather_data:
        city_name = (weather.get("city_name") or "").strip()
        country_code = (weather.get("country_code") or "").strip().upper()
        if not city_name or not country_code:
            continue

        location = get_or_create_location(
            city_name=city_name,
            country_code=country_code,
            latitude=weather["lat"],
            longitude=weather["lon"],
        )
        reading = WeatherReading.objects.create(
            user=user,
            location=location,
            city_name=city_name,
            country_code=country_code,
            latitude=Decimal(str(weather["lat"])),
            longitude=Decimal(str(weather["lon"])),
            temperature=Decimal(str(weather["temp"])),
            feels_like_temperature=Decimal(str(weather["app_temp"])),
        )
        saved_weather.append(
            {
                "city_name": reading.city_name,
                "country_code": reading.country_code,
                "lat": reading.latitude,
                "lon": reading.longitude,
                "temp": reading.temperature,
                "app_temp": reading.feels_like_temperature,
            }
        )

    return saved_weather


def calculate_and_save_average(user, city=None, latitude=None, longitude=None):
    location_input = validate_location_input(
        city,
        latitude,
        longitude,
    )
    location = resolve_location(**location_input)
    result = WeatherReading.objects.filter(user=user, location=location).aggregate(
        average=Avg("temperature"),
        count=Count("id"),
    )
    average = result["average"]
    count = result["count"]

    if average is not None:
        average = round(average, 2)
        TemperatureAverage.objects.create(
            user=user,
            location=location,
            latitude=location.latitude,
            longitude=location.longitude,
            average_temperature=average,
            count=count,
        )

    return {
        "average": average,
        "count": count,
    }


def get_weather_history(user):
    readings = WeatherReading.objects.filter(user=user).order_by("-created_at")
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
    return weather_data
