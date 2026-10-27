from decimal import Decimal
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import TestCase
from weather.models import Location, WeatherReading, TemperatureAverage
from weather.services import (
    fetch_and_save_weather,
    get_or_create_location,
    calculate_and_save_average,
    get_weather_history,
)

User = get_user_model()


class WeatherServiceIntegrationTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword123",
        )

    @patch("weather.services.fetch_weather_data")
    def test_fetch_and_save_weather(self, mock_fetch_weather):
        mock_fetch_weather.return_value = [
            {
                "city_name": "Berlin",
                "country_code": "de",
                "lat": 52.52,
                "lon": 13.405,
                "temp": 18.5,
                "app_temp": 17.8,
            }
        ]

        result = fetch_and_save_weather(
            user=self.user,
            city="Berlin",
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(WeatherReading.objects.count(), 1)
        self.assertEqual(Location.objects.count(), 1)

        reading = WeatherReading.objects.get()

        self.assertEqual(reading.user, self.user)
        self.assertEqual(reading.city_name, "Berlin")
        self.assertEqual(reading.country_code, "DE")
        self.assertEqual(reading.temperature, Decimal("18.5"))
        self.assertEqual(
            reading.feels_like_temperature,
            Decimal("17.8"),
        )

        mock_fetch_weather.assert_called_once_with(
            city="Berlin",
            latitude=None,
            longitude=None,
        )

    def test_get_or_create_location_reuses_existing_location(self):
        first_location = get_or_create_location(
            city_name="Berlin",
            country_code="de",
            latitude="52.520000",
            longitude="13.405000",
        )

        second_location = get_or_create_location(
            city_name=" Berlin ",
            country_code="DE",
            latitude="52.520000",
            longitude="13.405000",
        )

        self.assertEqual(first_location.pk, second_location.pk)
        self.assertEqual(Location.objects.count(), 1)

    @patch("weather.services.fetch_weather_data")
    def test_calculate_and_save_average(self, mock_fetch_weather):
        location = Location.objects.create(
            city_name="Berlin",
            city_name_normalized="berlin",
            country_code="DE",
            latitude=Decimal("52.520000"),
            longitude=Decimal("13.405000"),
        )

        WeatherReading.objects.create(
            user=self.user,
            location=location,
            city_name="Berlin",
            country_code="DE",
            latitude=Decimal("52.520000"),
            longitude=Decimal("13.405000"),
            temperature=Decimal("10.00"),
            feels_like_temperature=Decimal("9.00"),
        )

        WeatherReading.objects.create(
            user=self.user,
            location=location,
            city_name="Berlin",
            country_code="DE",
            latitude=Decimal("52.520000"),
            longitude=Decimal("13.405000"),
            temperature=Decimal("20.00"),
            feels_like_temperature=Decimal("19.00"),
        )

        mock_fetch_weather.return_value = [
            {
                "city_name": "Berlin",
                "country_code": "DE",
                "lat": 52.52,
                "lon": 13.405,
                "temp": 15.0,
                "app_temp": 14.0,
            }
        ]

        result = calculate_and_save_average(
            user=self.user,
            city="Berlin",
        )

        self.assertEqual(result["average"], Decimal("15.00"))
        self.assertEqual(result["count"], 2)

        saved_average = TemperatureAverage.objects.get()

        self.assertEqual(saved_average.user, self.user)
        self.assertEqual(saved_average.location, location)
        self.assertEqual(
            saved_average.average_temperature,
            Decimal("15.00"),
        )
        self.assertEqual(saved_average.count, 2)

    def test_get_weather_history_filters_by_city(self):
        berlin = Location.objects.create(
            city_name="Berlin",
            city_name_normalized="berlin",
            country_code="DE",
            latitude=Decimal("52.520000"),
            longitude=Decimal("13.405000"),
        )

        paris = Location.objects.create(
            city_name="Paris",
            city_name_normalized="paris",
            country_code="FR",
            latitude=Decimal("48.856600"),
            longitude=Decimal("2.352200"),
        )

        WeatherReading.objects.create(
            user=self.user,
            location=berlin,
            city_name="Berlin",
            country_code="DE",
            latitude=berlin.latitude,
            longitude=berlin.longitude,
            temperature=Decimal("18.50"),
            feels_like_temperature=Decimal("17.80"),
        )

        WeatherReading.objects.create(
            user=self.user,
            location=paris,
            city_name="Paris",
            country_code="FR",
            latitude=paris.latitude,
            longitude=paris.longitude,
            temperature=Decimal("22.00"),
            feels_like_temperature=Decimal("22.50"),
        )

        result = get_weather_history(
            user=self.user,
            filters={"city": "ber"},
        )

        self.assertEqual(len(result["weather_data"]), 1)
        self.assertEqual(
            result["weather_data"][0]["city_name"],
            "Berlin",
        )
        self.assertEqual(result["pagination"]["total_records"], 1)
        self.assertEqual(result["errors"], {})
