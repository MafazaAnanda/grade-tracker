from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime

def landing_page_view(request):
    context = {'message' : 'Selamat Datang!'}
    return render(request, 'landing_page.html', context)

def register_view(request):
    form = UserCreationForm()
    
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Akun Berhasil Dibuat!")
        
    context = {'form': form}
    return render(request, 'register.html', context)

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success("Anda Berhasil Login")
            response = HttpResponseRedirect(reverse("grade_tracker:dashboard"))
            response.set_cookie('last_login', str(datetime.datetime.now()))
            return response
        else:
            messages.error("Username atau Password Anda Invalid!")
        
    else:
        form = AuthenticationForm(request)
    
    context = {'form': form}
    return render(request, "login.html", context)

def logout_view(request):
    logout(request)
    response = HttpResponseRedirect(reverse("grade_tracker:landing_page"))
    response.delete_cookie('last_login')
    return response