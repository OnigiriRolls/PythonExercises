from unittest import TestCase
from weather.services import validate_location_input
from decimal import Decimal


class ValidateLocationInputTests(TestCase):

    def test_valid_city(self):
        result = validate_location_input(city="  Berlin  ")

        self.assertEqual(result["city"], "Berlin")
        self.assertIsNone(result["latitude"])
        self.assertIsNone(result["longitude"])

    def test_missing_city_and_coordinates(self):
        with self.assertRaises(ValueError):
            validate_location_input()

    def test_only_one_coordinate_provided(self):
        with self.assertRaises(ValueError):
            validate_location_input(latitude="48.13")

    def test_latitude_out_of_range(self):
        with self.assertRaises(ValueError):
            validate_location_input(
                latitude="91",
                longitude="25",
            )

    def test_valid_coordinates(self):
        result = validate_location_input(
            latitude="48.13",
            longitude="11.58",
        )

        self.assertEqual(result["latitude"], Decimal("48.13"))
        self.assertEqual(result["longitude"], Decimal("11.58"))
        self.assertIsNone(result["city"])
