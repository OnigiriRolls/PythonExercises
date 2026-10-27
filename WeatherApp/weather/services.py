import os
import re
import requests

from decimal import Decimal, InvalidOperation
from django.conf import settings
from django.db.models import Avg, Count

from weather.forms import WeatherHistoryFilterForm
from .models import Location, WeatherReading, TemperatureAverage
from django.core.paginator import Paginator


def validate_location_input(city="", latitude="", longitude=""):
    city = (city or "").strip()
    latitude = (latitude or "").strip()
    longitude = (longitude or "").strip()

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


def get_weather_history(
    user,
    filters={},
    page=1,
    page_size=5,
):
    input_data = {
        **filters,
        "page": page,
    }
    form = WeatherHistoryFilterForm(input_data)
    if not form.is_valid():
        return {
            "weather_data": [],
            "pagination": {
                "current_page": 1,
                "total_pages": 0,
                "total_records": 0,
                "has_next": False,
                "has_previous": False,
            },
            "errors": form.errors.get_json_data(),
        }
    validated_data = form.cleaned_data

    readings = WeatherReading.objects.filter(user=user)

    city = (validated_data.get("city") or "").strip()
    if city:
        readings = readings.filter(city_name__icontains=city)

    country = (validated_data.get("country") or "").strip()
    if country:
        readings = readings.filter(country_code__icontains=country)

    latitude = (validated_data.get("latitude") or "").strip()
    if latitude:
        readings = readings.filter(latitude=latitude)

    longitude = (validated_data.get("longitude") or "").strip()
    if longitude:
        readings = readings.filter(longitude=longitude)

    temperature_min = (validated_data.get("temperature_min") or "").strip()
    temperature_max = (validated_data.get("temperature_max") or "").strip()
    if temperature_min:
        readings = readings.filter(temperature__gte=temperature_min)
    if temperature_max:
        readings = readings.filter(temperature__lte=temperature_max)

    feels_like_min = (validated_data.get("feels_like_min") or "").strip()
    feels_like_max = (validated_data.get("feels_like_max") or "").strip()
    if feels_like_min:
        readings = readings.filter(feels_like_temperature__gte=feels_like_min)
    if feels_like_max:
        readings = readings.filter(feels_like_temperature__lte=feels_like_max)

    readings = readings.order_by("-created_at")
    paginator = Paginator(readings, page_size)
    page_obj = paginator.get_page(validated_data.get("page") or 1)
    weather_data = [
        {
            "city_name": reading.city_name,
            "country_code": reading.country_code,
            "lat": reading.latitude,
            "lon": reading.longitude,
            "temp": reading.temperature,
            "app_temp": reading.feels_like_temperature,
        }
        for reading in page_obj.object_list
    ]
    return {
        "weather_data": weather_data,
        "pagination": {
            "current_page": page_obj.number,
            "total_pages": paginator.num_pages,
            "total_records": paginator.count,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous(),
        },
        "errors": {},
    }
