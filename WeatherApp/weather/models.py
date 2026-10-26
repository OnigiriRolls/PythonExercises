from django.db import models
from django.conf import settings


# Create your models here.
class Location(models.Model):
    city_name = models.CharField(max_length=100)
    city_name_normalized = models.CharField(max_length=100)
    country_code = models.CharField(max_length=2)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["city_name_normalized", "country_code"],
                name="unique_normalized_city_country",
            )
        ]

    def __str__(self):
        return f"{self.city_name}, {self.country_code}"


class WeatherReading(models.Model):
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name="weather_readings",
        null=True,
        blank=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="weather_readings",
    )
    city_name = models.CharField(max_length=100, blank=True)
    country_code = models.CharField(max_length=2, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    temperature = models.DecimalField(max_digits=6, decimal_places=2)
    feels_like_temperature = models.DecimalField(max_digits=6, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.city_name}: {self.temperature}°C"


class TemperatureAverage(models.Model):
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name="temperature_averages",
        null=True,
        blank=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="temperature_averages",
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    average_temperature = models.DecimalField(max_digits=6, decimal_places=2)
    count = models.PositiveIntegerField()
    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Average: {self.average_temperature}°C"
