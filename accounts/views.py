from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login

from .forms import SingUpForm

def signup(request):
    if request.user.is_authenticated:
        return redirect("movies:list")
    form = SingUpForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)

        messages.success(request, f"Welcome, {user.username}")
        return redirect("movies:list")
    return render(request , "registration/signup.html", {"form": form})