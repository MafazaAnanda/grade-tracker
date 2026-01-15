from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from grade_tracker.models import MataKuliah, KomponenPenilaian, Semester
from grade_tracker.forms import MataKuliahForm, KomponenPenilaianForm
import datetime
import json

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
    
    context = {
        'mata_kuliah' : mata_kuliah_list,
        'last_login' : request.COOKIES.get('last_login', 'Never')
    }

    return render(request, 'dashboard.html', context)

@login_required
def create_mata_kuliah_view(request):
    form = MataKuliahForm(request.POST or None)
    
    if request.method == "POST" and form.is_valid():
        mata_kuliah_entry = form.save(commit=False)
        mata_kuliah_entry.user = request.user
        mata_kuliah_entry.save()
        return redirect('grade_tracker:dashboard')
    
    context = {'form' : form}
    return render(request, 'create_mata_kuliah.html', context)

@csrf_exempt
@login_required
@require_http_methods(["PATCH", "PUT"])
def edit_mata_kuliah_view(request, mata_kuliah_id):
    try:
        mata_kuliah = get_object_or_404(MataKuliah, pk=mata_kuliah_id)

        if mata_kuliah.user != request.user:
            return JsonResponse({
                'status': 'error',
                'message':'Anda Tidak Memiliki Akses untuk Mengedit Mata Kuliah Ini!'
            }, status=403)
        
        data = json.loads(request.body)

        mata_kuliah.nama = data.get('nama', mata_kuliah.nama)
        mata_kuliah.sks = data.get('sks', mata_kuliah.sks)
        mata_kuliah.save()

        return JsonResponse({
            'status': 'success',
            'message': "Mata Kuliah Berhasil Diedit",
            'data': {
                'id': str(mata_kuliah_id),
                'nama': mata_kuliah.nama,
                'sks': mata_kuliah.sks
            }
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid'
        }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
@require_http_methods(["DELETE"])
def delete_mata_kuliah_view(request, mata_kuliah_id):
    try:
        mata_kuliah = get_object_or_404(MataKuliah, pk=mata_kuliah_id)

        if mata_kuliah.user != request.user:
            return JsonResponse({
                'status': 'error',
                'message':'Anda Tidak Memiliki Akses untuk Menghapus Mata Kuliah Ini!'
            }, status=403)
        
        mata_kuliah.delete()
        return JsonResponse({
            'status': 'success',
            'message': "Mata Kuliah Berhasil Dihapus!"
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@login_required
def create_komponen_penilaian_view(request, mata_kuliah_id):
    mata_kuliah = get_object_or_404(MataKuliah, id=mata_kuliah_id, user=request.user)
    form = KomponenPenilaianForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        komponen_penilaian_entry = form.save(commit=False)
        komponen_penilaian_entry.mata_kuliah = mata_kuliah
        komponen_penilaian_entry.save()
        return redirect('grade_tracker:dashboard')
    
    context = {
        'form' : form,
        'mata_kuliah' : mata_kuliah,
    }

    return render(request, 'create_komponen_penilaian.html', context)