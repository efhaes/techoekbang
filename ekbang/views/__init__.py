# ekbang/views/auth.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Q
import datetime

from ekbang.models import Bumdes, BLTDD, Infrastruktur, Koperasi, KetahananPangan, Desa
from ekbang.forms.auth import LoginForm, BuatAkunDesaForm, DesaForm
from ekbang.decorators import kecamatan_required, desa_required

# --- HELPERS ---
def get_tahun_context(request):
    tahun_ini = datetime.date.today().year
    try:
        tahun = int(request.GET.get('tahun', tahun_ini))
    except (ValueError, TypeError):
        tahun = tahun_ini
    tahun_list = list(range(2025, tahun_ini + 5))
    return tahun, tahun_list

def redirect_by_role(user):
    if user.profile.is_kecamatan():
        return redirect('dashboard_kecamatan')
    return redirect('dashboard_desa')

# --- AUTH VIEWS ---
def login_view(request):
    if request.user.is_authenticated:
        return redirect_by_role(request.user)
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = authenticate(request, username=form.cleaned_data['username'], password=form.cleaned_data['password'])
        if user:
            login(request, user)
            return redirect_by_role(user)
        messages.error(request, "Username atau password salah.")
    return render(request, 'auth/login.html', {'form': form})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
    return redirect('login')

# --- KECAMATAN VIEWS ---
@login_required
@kecamatan_required
def dashboard_kecamatan(request):
    stats = {
        'bumdes': Bumdes.objects.aggregate(total=Count('id'), pending=Count('id', filter=Q(status='diajukan'))),
        'blt': BLTDD.objects.aggregate(total=Count('id'), pending=Count('id', filter=Q(status='diajukan'))),
        'infra': Infrastruktur.objects.aggregate(total=Count('id'), pending=Count('id', filter=Q(status='diajukan'))),
        'koperasi': Koperasi.objects.aggregate(total=Count('id'), pending=Count('id', filter=Q(status='diajukan'))),
        'pangan': KetahananPangan.objects.aggregate(total=Count('id'), pending=Count('id', filter=Q(status='diajukan'))),
    }
    total_pending_all = sum(s['pending'] for s in stats.values())
    desa_qs = Desa.objects.annotate(jml=Count('bumdes', filter=~Q(bumdes__status='draft'))).order_by('-jml')[:10]
    
    context = {
        'stats': stats,
        'total_pending_all': total_pending_all,
        'desa_labels': [d.nama for d in desa_qs],
        'counts': [d.jml for d in desa_qs],
    }
    return render(request, 'kecamatan/dashboard.html', context)

@login_required
@kecamatan_required
def buat_akun_desa(request):
    form = BuatAkunDesaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Akun desa berhasil dibuat.")
        return redirect('buat_akun_desa')
    return render(request, 'auth/buat_akun_desa.html', {'form': form})

@login_required
@kecamatan_required
def desa_create(request):
    form = DesaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Data desa berhasil ditambahkan.")
        return redirect('desa_create')
    return render(request, 'kecamatan/desa_form.html', {'form': form})

# --- DESA VIEWS ---
@login_required
@desa_required
def dashboard_desa(request):
    desa = request.user.profile.desa
    context = {'desa': desa}
    return render(request, 'dashboard_desa.html', context)

# --- ADDITIONAL ---
@login_required
@kecamatan_required
def review_list(request):
    return render(request, 'review_list.html')

@login_required
@kecamatan_required
def notifikasi_count(request):
    return JsonResponse({'status': 'ok'})