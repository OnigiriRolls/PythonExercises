from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .services import fetch_and_save_weather, calculate_and_save_average


@login_required
def get_temperatures_view(request):
    if request.method != "POST":
        return JsonResponse(
            {"api_error": "Method not allowed."},
            status=405,
        )

    try:
        weather_data = fetch_and_save_weather()
    except ValueError as error:
        return JsonResponse({"api_error": str(error)}, status=400)
    except Exception:
        return JsonResponse(
            {"api_error": "Could not retrieve weather data. Please try again."},
            status=500,
        )

    if not weather_data:
        return JsonResponse(
            {"api_error": "No weather data was returned."},
            status=200,
        )

    return JsonResponse(
        {
            "weather_data": weather_data,
            "api_error": None,
        }
    )


@login_required
def get_average_view(request):
    if request.method != "POST":
        return JsonResponse(
            {"api_error": "Method not allowed."},
            status=405,
        )

    result = calculate_and_save_average()

    return JsonResponse(
        {
            **result,
            "api_error": None,
        }
    )
