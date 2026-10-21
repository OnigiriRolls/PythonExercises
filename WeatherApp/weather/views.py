from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.decorators.http import require_POST, require_GET


@require_GET
def main_page_view(request):
    return render(request, "login.html")


@require_POST
def login_user(request):
    username = request.POST.get("username", "").strip()
    password = request.POST.get("password", "")
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect("home")

    error = "Invalid username or password."
    return render(request, "login.html", {"error": error})


@require_GET
def register_view(request):
    return render(request, "register.html")


@require_POST
def register(request):
    error = None

    username = request.POST.get("username", "").strip()
    password = request.POST.get("password", "")
    confirm_password = request.POST.get("confirm_password", "")

    if not username or not password or not confirm_password:
        error = "All fields are required."
    elif password != confirm_password:
        error = "Passwords do not match."
    elif User.objects.filter(username=username).exists():
        error = "This username is already taken."
    else:
        User.objects.create_user(username=username, password=password)
        return redirect("main_page_view")

    return render(request, "register.html", {"error": error})


@require_GET
@login_required
def home_view(request):
    context = {"username": request.user.username}
    return render(request, "home.html", context)


@require_POST
def logout_view(request):
    logout(request)
    return redirect("main_page_view")
