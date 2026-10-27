from django.test import SimpleTestCase
from weather.forms import WeatherHistoryFilterForm


class WeatherHistoryFilterFormTests(SimpleTestCase):

    def test_valid_filters(self):
        form = WeatherHistoryFilterForm(
            data={
                "city": "Berlin",
                "country": "DE",
                "temperature_min": "10",
                "temperature_max": "25",
                "page": "1",
            }
        )

        self.assertTrue(form.is_valid(), form.errors)

    def test_country_too_long(self):
        form = WeatherHistoryFilterForm(
            data={
                "country": "DEU",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("country", form.errors)

    def test_temperature_max_less_than_min(self):
        form = WeatherHistoryFilterForm(
            data={
                "temperature_min": "25",
                "temperature_max": "10",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("temperature_max", form.errors)
