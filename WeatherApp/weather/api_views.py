from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .services import (
    fetch_and_save_weather,
    calculate_and_save_average,
    get_weather_history,
)


@require_POST
@login_required
def get_temperatures_view(request):
    try:
        weather_data = fetch_and_save_weather(
            user=request.user,
            city=request.POST.get("city", ""),
            latitude=request.POST.get("latitude", ""),
            longitude=request.POST.get("longitude", ""),
        )
    except ValueError as error:
        return JsonResponse({"api_error": str(error)}, status=400)
    except Exception as ex:
        print(ex)
        return JsonResponse(
            {"api_error": ("Could not retrieve weather data. Please try again.")},
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


@require_POST
@login_required
def get_average_view(request):
    try:
        result = calculate_and_save_average(
            user=request.user,
            city=request.POST.get("city", ""),
            latitude=request.POST.get("latitude", ""),
            longitude=request.POST.get("longitude", ""),
        )
    except ValueError as error:
        return JsonResponse({"api_error": str(error)}, status=400)
    except Exception:
        return JsonResponse(
            {"api_error": ("Could not calculate the average. Please try again.")},
            status=500,
        )

    return JsonResponse(
        {
            **result,
            "api_error": None,
        }
    )


@require_POST
@login_required
def get_history_view(request):
    filters = {
        "city": request.POST.get("city", ""),
        "country": request.POST.get("country", ""),
        "latitude": request.POST.get("latitude", ""),
        "longitude": request.POST.get("longitude", ""),
        "temperature_min": request.POST.get("temperature_min", ""),
        "temperature_max": request.POST.get("temperature_max", ""),
        "feels_like_min": request.POST.get("feels_like_min", ""),
        "feels_like_max": request.POST.get("feels_like_max", ""),
    }
    page = request.POST.get("page", 1)
    result = get_weather_history(
        user=request.user,
        filters=filters,
        page=page,
    )
    return JsonResponse(
        {
            "weather_data": result["weather_data"],
            "pagination": result["pagination"],
            "api_error": None,
        }
    )
