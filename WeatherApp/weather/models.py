from django.db import models

# Create your models here.


class WeatherReading(models.Model):
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
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    average_temperature = models.DecimalField(max_digits=6, decimal_places=2)

    count = models.PositiveIntegerField()

    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Average: {self.average_temperature}°C"
