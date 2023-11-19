from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import UserRegisterForm
from .singleton import AuthenticationSingleton

auth_singleton = AuthenticationSingleton()

def RegisterView(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        print(form.is_valid())
        if form.is_valid():
            new_user = form.save()
            username = form.cleaned_data.get("username")
            messages.success(request, f"Hey {username}, your account was created successfully.")
            success, message = auth_singleton.login_user(request, email=form.cleaned_data['email'], password=form.cleaned_data['password1'])
            if success:
                return redirect("account:account")
            else:
                messages.warning(request, message)
        else:
            messages.warning(request, "Password must contain at least 8 characters (number and alphabet)")

    if request.user.is_authenticated:
        messages.warning(request, f"You are already logged in.")
        return redirect("account:account")

    else:
        form = UserRegisterForm()
    context = {
        "form": form
    }
    return render(request, "userauths/sign-up.html", context)

def LoginView(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        success, message = auth_singleton.login_user(request, email=email, password=password)
        if success:
            messages.success(request, message)
            return redirect("account:account")
        else:
            messages.warning(request, message)

    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in")
        return redirect("account:account")

    return render(request, "userauths/sign-in.html")

def logoutView(request):
    success, message = auth_singleton.logout_user(request)
    if success:
        messages.success(request, message)
    else:
        messages.warning(request, message)
    return redirect("userauths:sign-in")
