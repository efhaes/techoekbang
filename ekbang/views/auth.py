from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Q
import datetime
# Tambahkan ini di deretan import paling atas
from django.core.mail import EmailMessage
from django.conf import settings
from ekbang.models import UserProfile # Menambahkan UserProfile ke import models kamu
# Import Models & Forms
from ekbang.models import Bumdes, BLTDD, Infrastruktur, Koperasi, KetahananPangan, Desa
from ekbang.forms.auth import LoginForm, BuatAkunDesaForm, DesaForm
from ekbang.decorators import kecamatan_required

# ─────────────────────────────────────────
# HELPER
# ─────────────────────────────────────────

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

# ─────────────────────────────────────────
# AUTH & ACCOUNT MANAGEMENT
# ─────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect_by_role(request.user)

    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password'],
        )
        if user:
            login(request, user)
            return redirect_by_role(user)
        messages.error(request, "Username atau password salah.")

    return render(request, 'auth/login.html', {'form': form})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
    return redirect('login')

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

# ─────────────────────────────────────────
# DASHBOARD KECAMATAN
# ─────────────────────────────────────────

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

    total_pending_all = sum(item['pending'] for item in stats.values())

    desa_qs = Desa.objects.annotate(
        jml_pengajuan=(
            Count('bumdes', distinct=True) + 
            Count('bltdd', distinct=True) + 
            Count('infrastruktur', distinct=True)
        )
    ).order_by('-jml_pengajuan')[:10]

    context = {
        'stats': stats,
        'total_pending_all': total_pending_all,
        'desa_labels': [d.nama for d in desa_qs],
        'desa_counts': [d.jml_pengajuan for d in desa_qs],
        'tahun_ini': datetime.date.today().year,
    }
    return render(request, 'dashboard_kecamatan.html', context)

# ─────────────────────────────────────────
# DASHBOARD DESA
# ─────────────────────────────────────────
# helper biar gak repetitif
def get_data(model, desa, tahun):
    return model.objects.filter(
        desa=desa,
        tahun_anggaran=tahun
    ).first()


from django.db.models import Count, Q

@login_required
def dashboard_desa(request):
    if not request.user.profile.is_desa():
        return redirect('dashboard_kecamatan')

    desa = request.user.profile.desa
    tahun_ini = datetime.date.today().year

    def count_status(model):
        return model.objects.filter(desa=desa, tahun_anggaran=tahun_ini).aggregate(
            draft=Count('id', filter=Q(status='draft')),
            diajukan=Count('id', filter=Q(status='diajukan')),
            disetujui=Count('id', filter=Q(status='disetujui')),
            ditolak=Count('id', filter=Q(status='ditolak')),
        )

    context = {
        'desa': desa,
        'tahun': tahun_ini,

        'bumdes': Bumdes.objects.filter(desa=desa, tahun_anggaran=tahun_ini).last(),
        'bltdd': BLTDD.objects.filter(desa=desa, tahun_anggaran=tahun_ini).last(),
        'infrastruktur': Infrastruktur.objects.filter(desa=desa, tahun_anggaran=tahun_ini).last(),
        'koperasi': Koperasi.objects.filter(desa=desa, tahun_anggaran=tahun_ini).last(),
        'ketahanan': KetahananPangan.objects.filter(desa=desa, tahun_anggaran=tahun_ini).last(),

        'stats': {
            'bumdes': count_status(Bumdes),
            'bltdd': count_status(BLTDD),
            'infra': count_status(Infrastruktur),
            'koperasi': count_status(Koperasi),
            'ketahanan': count_status(KetahananPangan),
        }
    }

    return render(request, 'dashboard_desa.html', context)

# ─────────────────────────────────────────
# NOTIFIKASI
# ─────────────────────────────────────────

@login_required
@kecamatan_required
def notifikasi_count(request):
    items = []
    def gather(queryset, modul, field_name):
        for obj in queryset.select_related('desa').filter(status='diajukan').order_by('-tanggal_diajukan')[:3]:
            items.append({
                'modul': modul,
                'desa': obj.desa.nama,
                'nama': getattr(obj, field_name, '-'),
                'waktu': obj.tanggal_diajukan
            })

    gather(Bumdes.objects, 'BUMDes', 'nama_bumdes')
    gather(BLTDD.objects, 'BLT Dana Desa', 'nomor_sk')
    gather(Infrastruktur.objects, 'Infrastruktur', 'kegiatan')

    items.sort(key=lambda x: x['waktu'] or timezone.now(), reverse=True)
    
    for item in items:
        item['waktu'] = item['waktu'].strftime('%d %b, %H:%M') if item['waktu'] else '-'

    return JsonResponse({'count': len(items), 'items': items[:5]})
# ─────────────────────────────────────────
# REVIEW LIST — Kecamatan lihat semua pengajuan
# ─────────────────────────────────────────

@login_required
@kecamatan_required
def review_list(request):
    tahun, tahun_list = get_tahun_context(request)
    
    # Ambil semua data yang statusnya 'diajukan' (Menunggu Review)
    # Gunakan select_related('desa') agar query lebih ringan (tidak N+1)
    context = {
        'bumdes_list': Bumdes.objects.filter(status='diajukan', tahun_anggaran=tahun).select_related('desa'),
        'bltdd_list': BLTDD.objects.filter(status='diajukan', tahun_anggaran=tahun).select_related('desa'),
        'infrastruktur_list': Infrastruktur.objects.filter(status='diajukan', tahun_anggaran=tahun).select_related('desa'),
        'koperasi_list': Koperasi.objects.filter(status='diajukan', tahun_anggaran=tahun).select_related('desa'),
        'ketahanan_list': KetahananPangan.objects.filter(status='diajukan', tahun_anggaran=tahun).select_related('desa'),
        'tahun': tahun,
        'tahun_list': tahun_list,
    }
    return render(request, 'kecamatan/review_list.html', context)

# Tambahkan ini di bagian bawah views.py kamu

import datetime
from itertools import chain

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings





@login_required
@kecamatan_required
def kirim_peringatan_masal(request):
    """
    Mengirim email peringatan ke desa yang belum upload laporan
    per modul (dinamis).
    """

    # 🚫 hanya POST
    if request.method != "POST":
        messages.warning(request, "Akses ditolak. Gunakan tombol yang tersedia.")
        return redirect('dashboard_kecamatan')

    tahun_ini = datetime.date.today().year

    # 🔍 cari desa + modul yang belum
    desa_belum = []

    for desa in Desa.objects.all():

        modul_belum = []

        if not Bumdes.objects.filter(
            desa=desa,
            tahun_anggaran=tahun_ini,
            status__in=['diajukan', 'disetujui']
        ).exists():
            modul_belum.append('BUMDes')

        if not BLTDD.objects.filter(
            desa=desa,
            tahun_anggaran=tahun_ini,
            status__in=['diajukan', 'disetujui']
        ).exists():
            modul_belum.append('BLT Dana Desa')

        if not Infrastruktur.objects.filter(
            desa=desa,
            tahun_anggaran=tahun_ini,
            status__in=['diajukan', 'disetujui']
        ).exists():
            modul_belum.append('Infrastruktur')

        if not KetahananPangan.objects.filter(
            desa=desa,
            tahun_anggaran=tahun_ini,
            status__in=['diajukan', 'disetujui']
        ).exists():
            modul_belum.append('Ketahanan Pangan')

        if not Koperasi.objects.filter(
            desa=desa,
            tahun_anggaran=tahun_ini,
            status__in=['diajukan', 'disetujui']
        ).exists():
            modul_belum.append('Koperasi')

        # kalau ada yang belum
        if modul_belum:
            desa_belum.append({
                'desa': desa,
                'modul': modul_belum
            })

    # 🔗 URL login
    login_url = request.build_absolute_uri(reverse('login'))

    # 🔥 ambil semua admin desa sekaligus (biar hemat query)
    admin_map = {
        up.desa_id: up
        for up in UserProfile.objects.filter(
            role='admin_desa'
        ).select_related('user')
    }

    count_success = 0
    count_failed = 0

    # 📩 kirim email
    for item in desa_belum:
        desa = item['desa']
        modul_belum = item['modul']

        admin_desa = admin_map.get(desa.id)

        # skip kalau ga ada email
        if not admin_desa or not admin_desa.user.email:
            continue

        # validasi email
        try:
            validate_email(admin_desa.user.email)
        except ValidationError:
            continue

        # 🧠 format list modul
        modul_text = "\n".join([f"- {m}" for m in modul_belum])

        isi_pesan = f"""
Yth. Admin Desa {desa.nama},

Berdasarkan sistem Eksbang Kecamatan, desa Anda BELUM mengunggah laporan
Tahun Anggaran {tahun_ini} pada modul berikut:

{modul_text}

Mohon segera melakukan upload melalui link berikut:
{login_url}

Terima kasih.
Admin Kecamatan
        """

        email = EmailMessage(
            subject=f"PENGINGAT ({len(modul_belum)} Modul) - {desa.nama}",
            body=isi_pesan,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[admin_desa.user.email],
        )

        try:
            email.send(fail_silently=True)
            count_success += 1
            print(f"[SUCCESS] {desa.nama} -> {admin_desa.user.email}")

        except Exception as e:
            print(f"[ERROR] {desa.nama} -> {e}")
            count_failed += 1

    # 📊 feedback
    if count_success > 0:
        messages.success(
            request,
            f"✅ {count_success} email berhasil dikirim. ❌ {count_failed} gagal."
        )
    else:
        messages.info(
            request,
            "Semua desa sudah melapor atau tidak ada email valid."
        )

    return redirect('dashboard_kecamatan')