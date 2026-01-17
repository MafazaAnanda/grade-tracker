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
            response = HttpResponseRedirect(reverse("grade_tracker:home"))
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
def home_view(request):
    mata_kuliah_list = MataKuliah.objects.filter(user=request.user)
    
    context = {
        'mata_kuliah_list' : mata_kuliah_list,
        'last_login' : request.COOKIES.get('last_login', 'Never')
    }

    return render(request, 'home.html', context)

@login_required
def mata_kuliah_details_view(request, mata_kuliah_id):
    mata_kuliah = get_object_or_404(MataKuliah, pk=mata_kuliah_id, user=request.user)
    komponen_penilaian_list = KomponenPenilaian.objects.filter(mata_kuliah=mata_kuliah)

    context = {
        'mata_kuliah': mata_kuliah,
        'komponen_penilaian_list': komponen_penilaian_list 
    }

    return render(request, 'mata_kuliah_details.html', context)

@csrf_exempt
@login_required
@require_POST
def create_mata_kuliah_view(request):
    try:
        data = json.loads(request.body)

        nama = data.get('nama')
        sks = data.get('sks')
        
        if not nama:
            return JsonResponse({
                'status': 'error',
                'code': 'INVALID_INPUT',
                'message': 'Nama Mata Kuliah Harus Diisi!'
            })
        
        if not sks or sks == 0:
            return JsonResponse({
                'status': 'error',
                'code': 'INVALID_INPUT',
                'message': 'Jumlah SKS Invalid!'
            })
            
        mata_kuliah = MataKuliah.objects.create(
            user=request.user,
            nama=nama,
            sks=sks
        )

        return JsonResponse({
            'status': 'success',
            'message': 'Mata Kuliah Berhasil Ditambahkan!',
            'data': {
                'id': str(mata_kuliah.id),
                'nama': mata_kuliah.nama,
                'sks': mata_kuliah.sks
            }
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'code': 'INVALID_JSON',
            'message': 'Invalid JSON'
        }, status=400)
    
    except Exception:
        return JsonResponse({
            'status': 'error',
            'code': 'INTERNAL_SERVER_ERROR',
            'message': 'Mata Kuliah Gagal Ditambahkan!'
        }, status=500)

@csrf_exempt
@login_required
@require_http_methods(["PATCH", "PUT"])
def update_mata_kuliah_view(request, mata_kuliah_id):
    try:
        mata_kuliah = get_object_or_404(MataKuliah, pk=mata_kuliah_id)

        if mata_kuliah.user != request.user:
            return JsonResponse({
                'status': 'error',
                'code': 'PERMISSION_DENIED',
                'message':'Anda Tidak Memiliki Akses untuk Mengedit Mata Kuliah Ini!'
            }, status=403)
        
        data = json.loads(request.body)

        mata_kuliah.nama = data.get('nama', mata_kuliah.nama)
        mata_kuliah.sks = data.get('sks', mata_kuliah.sks)

        if not mata_kuliah.nama:
            return JsonResponse({
                'status': 'error',
                'code': 'INVALID_INPUT',
                'message': 'Nama Mata Kuliah Harus Diisi!'
            })
        
        if not mata_kuliah.sks or mata_kuliah.sks <= 0:
            return JsonResponse({
                'status': 'error',
                'code': 'INVALID_INPUT',
                'message': 'Jumlah SKS Invalid'
            })

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
            'code': 'INVALID_JSON',
            'message': 'Format Data Invalid'
        }, status=400)
    
    except Exception:
        return JsonResponse({
            'status': 'error',
            'code': 'INTERNAL_SERVER_ERROR',
            'message': 'Mata Kuliah Gagal Diedit'
        }, status=500)

@csrf_exempt
@login_required
@require_http_methods(["DELETE"])
def delete_mata_kuliah_view(request, mata_kuliah_id):
    try:
        mata_kuliah = get_object_or_404(MataKuliah, pk=mata_kuliah_id)

        if mata_kuliah.user != request.user:
            return JsonResponse({
                'status': 'error',
                'code': 'PERMISSION_DENIED',
                'message':'Anda Tidak Memiliki Akses untuk Menghapus Mata Kuliah Ini!'
            }, status=403)
        
        mata_kuliah.delete()
        return JsonResponse({
            'status': 'success',
            'message': "Mata Kuliah Berhasil Dihapus!"
        })
    
    except Exception:
        return JsonResponse({
            'status': 'error',
            'code': 'INTERNAL SERVER_ERROR',
            'message': 'Mata Kuliah Gagal Dihapus!'
        }, status=500)

@csrf_exempt
@login_required
@require_POST
def create_komponen_penilaian_view(request, mata_kuliah_id):
    try:
        mata_kuliah = get_object_or_404(MataKuliah, id=mata_kuliah_id, user=request.user)

        data = json.loads(request.body)
        nama = data.get('nama')
        persentase = data.get('persentase')

        if not nama:
            return JsonResponse({
                'status': 'error',
                'code': 'INVALID_INPUT',
                'message': 'Nama Komponen Penilaian Harus Diisi!'
            })
        
        if persentase is None or persentase < 0 or persentase > 100:
            return JsonResponse({
                'status': 'error',
                'code': 'INVALID_INPUT',
                'message': 'Nilai Persentase Harus Antara 0-100!'
            })
        
        komponen_penilaian = KomponenPenilaian.objects.create(
            mata_kuliah=mata_kuliah,
            nama=nama,
            persentase=persentase,
            nilai=data.get('nilai'),
            deadline=data.get('deadline'),
            sudah_selesai=data.get('sudah_selesai')
        )

        return JsonResponse({
            'status': 'success',
            'message': 'Komponen Penilaian Berhasil Ditambahkan!',
            'data': {
                'id': komponen_penilaian.id,
                'nama': komponen_penilaian.nama,
                'persentase': komponen_penilaian.persentase,
                'nilai': komponen_penilaian.nilai,
                'sudah_selesai': komponen_penilaian.sudah_selesai
            }
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'code': 'INVALID_JSON',
            'message': 'Invalid JSON'
        }, status=400)
    
    except Exception:
        return JsonResponse({
            'status':'error',
            'code': 'INTERNAL_SERVER_ERROR',
            'message': 'Komponen Penilaian Gagal Ditambahkan!'
        })

@csrf_exempt
@login_required
@require_http_methods(["PATCH", "PUT"])
def update_komponen_penilaian_view(request, komponen_penilaian_id):
    try:
        komponen_penilaian = get_object_or_404(KomponenPenilaian, pk=komponen_penilaian_id)
        
        if komponen_penilaian.mata_kuliah.user != request.user:
            return JsonResponse({
                    'status': 'error',
                    'code': 'PERMISSION_DENIED',
                    'message':'Anda Tidak Memiliki Akses untuk Mengedit Komponen Penilaian Ini!'
            }, status=403)
        
        data = json.loads(request.body)

        komponen_penilaian.nama = data.get('nama', komponen_penilaian.nama)
        komponen_penilaian.persentase = data.get('persentase', komponen_penilaian.persentase)
        komponen_penilaian.nilai = data.get('nilai', komponen_penilaian.nilai)
        komponen_penilaian.deadline = data.get('deadline', komponen_penilaian.deadline)
        komponen_penilaian.sudah_selesai = data.get('sudah_selesai', komponen_penilaian.sudah_selesai)

        if not komponen_penilaian.nama:
            return JsonResponse({
                'status': 'error',
                'code': 'INVALID_INPUT',
                'message': 'Nama Komponen Penilaian Harus Diisi!'
            })
        
        if (komponen_penilaian.persentase is None or komponen_penilaian.persentase < 0 
            or komponen_penilaian.persentase > 100):
            return JsonResponse({
                'status': 'error',
                'code': 'INVALID_INPUT',
                'message': 'Nilai Persentase Harus Antara 0-100!'
            })
        
        if komponen_penilaian.nilai is None or komponen_penilaian.nilai < 0:
            return JsonResponse({
                'status': 'error',
                'code': 'INVALID_INPUT',
                'message': 'Nilai Tidak Boleh Negatif'
            })
        
        komponen_penilaian.save()

        return JsonResponse({
            'status': 'success',
            'message': 'Komponen Penilaian Berhasil Diedit',
            'data': {
                'id': komponen_penilaian.id,
                'nama': komponen_penilaian.nama,
                'persentase': komponen_penilaian.persentase,
                'nilai': komponen_penilaian.nilai,
                'sudah_selesai': komponen_penilaian.sudah_selesai
            }
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'code': 'INVALID_JSON',
            'message': 'Invalid JSON'
        }, status=400)
    
    except Exception:
        return JsonResponse({
            'status': 'error',
            'code': 'INTERNAL_SERVER_ERROR',
            'message': 'Komponen Penilaian Gagal Diedit'
        }, status=500)

@csrf_exempt
@login_required
@require_http_methods(["DELETE"])
def delete_komponen_penilaian_view(request, komponen_penilaian_id):
    try:
        komponen_penilaian = get_object_or_404(KomponenPenilaian, pk=komponen_penilaian_id)

        if komponen_penilaian.mata_kuliah.user != request.user:
            return JsonResponse({
                    'status': 'error',
                    'code': 'PERMISSION_DENIED',
                    'message':'Anda Tidak Memiliki Akses untuk Menghapus Komponen Penilaian Ini!'
            }, status=403)
        
        komponen_penilaian.delete()
        return JsonResponse({
            'status': 'success',
            'message': "Komponen Penilaian Berhasil Dihapus!"
        })
    
    except Exception:
        return JsonResponse({
            'status': 'error',
            'code': 'INTERNAL_SERVER_ERROR',
            'message': 'Komponen Penilaian Gagal Diedit'
        }, status=500)