from decimal import Decimal
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from weather.models import WeatherReading

User = get_user_model()


class WeatherFeatureTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword123",
        )

    @patch("weather.api_views.fetch_and_save_weather")
    def test_authenticated_user_can_get_temperatures(self, mock_fetch_weather):
        mock_fetch_weather.return_value = [
            {
                "city_name": "Berlin",
                "country_code": "DE",
                "lat": Decimal("52.520000"),
                "lon": Decimal("13.405000"),
                "temp": Decimal("18.50"),
                "app_temp": Decimal("17.80"),
            }
        ]
        self.client.login(
            username="testuser",
            password="testpassword123",
        )

        response = self.client.post(
            reverse("get_temperatures"),
            {"city": "Berlin"},
        )

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIsNone(response_data["api_error"])
        self.assertEqual(len(response_data["weather_data"]), 1)
        self.assertEqual(
            response_data["weather_data"][0]["city_name"],
            "Berlin",
        )
        mock_fetch_weather.assert_called_once()

    def test_unauthenticated_user_is_redirected_to_login(self):
        response = self.client.post(
            reverse("get_temperatures"),
            {"city": "Berlin"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('get_temperatures')}",
            fetch_redirect_response=False,
        )
        self.assertEqual(WeatherReading.objects.count(), 0)
