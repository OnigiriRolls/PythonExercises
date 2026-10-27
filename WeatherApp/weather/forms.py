from django import forms


class WeatherHistoryFilterForm(forms.Form):
    city = forms.CharField(
        required=False,
        max_length=100,
    )

    country = forms.CharField(
        required=False,
        max_length=2,
    )

    latitude = forms.DecimalField(
        required=False,
        max_digits=9,
        decimal_places=6,
        min_value=-90,
        max_value=90,
    )

    longitude = forms.DecimalField(
        required=False,
        max_digits=9,
        decimal_places=6,
        min_value=-180,
        max_value=180,
    )

    temperature_min = forms.DecimalField(
        required=False,
        max_digits=6,
        decimal_places=2,
    )

    temperature_max = forms.DecimalField(
        required=False,
        max_digits=6,
        decimal_places=2,
    )

    feels_like_min = forms.DecimalField(
        required=False,
        max_digits=6,
        decimal_places=2,
    )

    feels_like_max = forms.DecimalField(
        required=False,
        max_digits=6,
        decimal_places=2,
    )

    page = forms.IntegerField(
        required=False,
        min_value=1,
        initial=1,
    )

    def clean(self):
        cleaned_data = super().clean()
        ranges = [
            ("temperature_min", "temperature_max"),
            ("feels_like_min", "feels_like_max"),
        ]
        for minimum_field, maximum_field in ranges:
            minimum = cleaned_data.get(minimum_field)
            maximum = cleaned_data.get(maximum_field)
            if minimum is not None and maximum is not None and minimum > maximum:
                self.add_error(
                    maximum_field,
                    "Maximum must be greater than or equal to minimum.",
                )

        return cleaned_data
