from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from grade_tracker.models import MataKuliah, KomponenPenilaian
from grade_tracker.forms import MataKuliahForm, KomponenPenilaianForm
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
            messages.success(request, "Anda Berhasil Login")
            response = HttpResponseRedirect(reverse("grade_tracker:dashboard"))
            response.set_cookie('last_login', str(datetime.datetime.now()))
            return response
        else:
            messages.error(request, "Username atau Password Anda Invalid!")
        
    else:
        form = AuthenticationForm(request)
    
    context = {'form': form}
    return render(request, "login.html", context)

def logout_view(request):
    logout(request)
    response = HttpResponseRedirect(reverse("grade_tracker:landing_page"))
    response.delete_cookie('last_login')
    return response

@login_required
def dashboard_view(request):
    mata_kuliah_list = MataKuliah.objects.filter(user=request.user)
    komponen_penilaian_list = KomponenPenilaian.objects.filter(mata_kuliah__user=request.user)
    
    context = {
        'mata_kuliah_list' : mata_kuliah_list,
        'komponen_penilaian_list' : komponen_penilaian_list,
        'last_login' : request.COOKIES.get('last_login', 'Never')
    }

    return render(request, 'dashboard.html', context)

@login_required
def create_mata_kuliah_view(request):
    form = MataKuliahForm(request.POST or None)
    
    if form.is_valid() and request.method == "POST":
        mata_kuliah_entry = form.save(commit=False)
        mata_kuliah_entry.user = request.user
        mata_kuliah_entry.save()
        return redirect('grade_tracker:dashboard')
    
    context = {'form' : form}
    return render(request, 'create_mata_kuliah.html', context)