from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Q
import datetime
from django.shortcuts import get_object_or_404 
from django.contrib.auth.models import User
# Tambahkan ini di deretan import paling atas
from django.core.mail import EmailMessage
from django.conf import settings
from ekbang.models import UserProfile # Menambahkan UserProfile ke import models kamu
# Import Models & Forms
from ekbang.models import Bumdes, BLTDD, Infrastruktur, Koperasi, KetahananPangan, Desa
from ekbang.forms.auth import LoginForm, BuatAkunDesaForm, DesaForm
from ekbang.decorators import kecamatan_required
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db import transaction
import uuid
from django.utils import timezone
from datetime import timedelta
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
        try:
            with transaction.atomic():

                # 1. Simpan User
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password'])
                user.is_active = False 
                user.save()

                # 2. Simpan Profile
                profile, created = UserProfile.objects.get_or_create(user=user)
                profile.role = 'admin_desa'
                profile.desa = form.cleaned_data.get('desa')
                profile.is_email_verified = False

                # 🔥 GENERATE TOKEN BARU
                profile.email_verification_token = uuid.uuid4()
                profile.token_created_at = timezone.now()

                profile.save()

                # 3. Link verifikasi
                uid = urlsafe_base64_encode(force_bytes(user.pk))

                verify_url = request.build_absolute_uri(
                    reverse('verifikasi_email', kwargs={
                        'uidb64': uid,
                        'token': str(profile.email_verification_token)
                    })
                )

                # 4. Kirim email
                context = {'user': user, 'verify_url': verify_url}
                html_content = render_to_string('emails/verifikasi_email_template.html', context)

                email = EmailMultiAlternatives(
                    subject='Aktivasi Akun Desa - Admin Eksbang',
                    body=strip_tags(html_content),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[user.email],
                )
                email.attach_alternative(html_content, "text/html")
                email.send(fail_silently=False)

            messages.success(request, f"Akun desa berhasil dibuat. Silakan verifikasi email {user.email}")
            return redirect('buat_akun_desa')

        except Exception as e:
            messages.error(request, f"Gagal mengirim email verifikasi: {str(e)}")

    return render(request, 'auth/buat_akun_desa.html', {'form': form})

def verifikasi_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        profile = user.profile
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if not user:
        messages.error(request, "User tidak ditemukan.")
        return redirect('login')

    # 🔥 CASE 1: TOKEN SAMA
    if str(profile.email_verification_token) == token:

        # 🔥 CEK EXPIRED
        if profile.token_created_at and timezone.now() > profile.token_created_at + timedelta(seconds=30):
            messages.error(request, "Maaf, link verifikasi anda sudah kadaluarsa.")
            return redirect('login')

        # ✅ VALID
        if user.is_active:
            messages.info(request, "Akun sudah aktif sebelumnya.")
        else:
            user.is_active = True
            profile.is_email_verified = True

            # invalidate token
            profile.email_verification_token = None
            profile.token_created_at = None

            user.save()
            profile.save()

            messages.success(request, "Email berhasil diverifikasi!")

        return redirect('login')

    else:
        # 🔥 CASE 2: TOKEN BERBEDA (kemungkinan link lama)
        if profile.email_verification_token:
            messages.error(request, "Maaf, link verifikasi ini sudah tidak berlaku. Silakan gunakan link terbaru dari email.")

        else:
            messages.error(request, "Link verifikasi tidak valid.")

        return redirect('login')


# Pastikan ini di-import di atas

@login_required
@kecamatan_required
def akun_desa_list(request):
    # Mengambil semua user yang memiliki role 'admin_desa' melalui UserProfile
    # Kita gunakan select_related agar query lebih efisien (tidak N+1)
    users_desa = User.objects.filter(profile__role='admin_desa').select_related('profile', 'profile__desa')
    
    return render(request, 'auth/akun_desa_list.html', {'users_desa': users_desa})

@login_required
@kecamatan_required
def edit_akun_desa(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    
    if request.method == 'POST':
        form = BuatAkunDesaForm(request.POST, instance=user)

        # password opsional
        form.fields['password'].required = False
        form.fields['konfirmasi_password'].required = False

        if form.is_valid():
            with transaction.atomic():
                updated_user = form.save(commit=False)

                # 🔥 HANDLE PASSWORD
                password = form.cleaned_data.get('password')
                konfirmasi = form.cleaned_data.get('konfirmasi_password')

                if password:
                    if password != konfirmasi:
                        messages.error(request, "Password dan konfirmasi tidak sama.")
                        return redirect(request.path)

                    updated_user.set_password(password)

                updated_user.save()

                # update profile
                profile = updated_user.profile
                profile.desa = form.cleaned_data.get('desa')
                profile.save()
            
            messages.success(request, f"Data akun {updated_user.username} berhasil diperbarui.")
            return redirect('akun_desa_list')

    else:
        form = BuatAkunDesaForm(
            instance=user,
            initial={'desa': user.profile.desa}
        )

        # password gak wajib diisi
        form.fields['password'].required = False
        form.fields['konfirmasi_password'].required = False
            
    return render(request, 'auth/edit_akun_desa.html', {
        'form': form,
        'user_edit': user
    })

@login_required
@kecamatan_required
def hapus_akun_desa(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(User, pk=user_id)
        username = user.username
        user.delete() # Ini otomatis menghapus UserProfile karena on_delete=CASCADE
        messages.success(request, f"Akun {username} berhasil dihapus.")
    return redirect('akun_desa_list')

@login_required
@kecamatan_required
def kirim_ulang_verifikasi(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    if user.is_active:
        messages.info(request, f"Akun {user.username} sudah aktif.")
        return redirect('akun_desa_list')

    try:
        with transaction.atomic():
            profile = user.profile

            # 🔥 GENERATE TOKEN BARU (INI YANG BENER)
            profile.email_verification_token = uuid.uuid4()
            profile.token_created_at = timezone.now()
            profile.save()

            uid = urlsafe_base64_encode(force_bytes(user.pk))

            verify_url = request.build_absolute_uri(
                reverse('verifikasi_email', kwargs={
                    'uidb64': uid,
                    'token': str(profile.email_verification_token)
                })
            )

            context = {'user': user, 'verify_url': verify_url}
            html_content = render_to_string('emails/verifikasi_email_template.html', context)

            email = EmailMultiAlternatives(
                subject='Kirim Ulang: Aktivasi Akun Desa',
                body=strip_tags(html_content),
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)

        messages.success(request, f"Link verifikasi baru telah dikirim ke {user.email}")

    except Exception as e:
        messages.error(request, f"Gagal mengirim email: {str(e)}")

    return redirect('akun_desa_list')


@login_required
@kecamatan_required
def desa_list(request):
    data = Desa.objects.all().order_by('-id')
    form = DesaForm()
    return render(request, 'auth/desa_list.html', {
        'data': data,
        'form': form
    })


@login_required
@kecamatan_required
def desa_create(request):
    if request.method == 'POST':
        form = DesaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Data desa berhasil ditambahkan.")
            return redirect('desa_list')
    else:
        form = DesaForm()

    return render(request, 'auth/buat_desa.html', {
        'form': form
    })


@login_required
@kecamatan_required
def desa_edit(request, id):
    desa = get_object_or_404(Desa, id=id)

    if request.method == 'POST':
        form = DesaForm(request.POST, instance=desa)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'})


@login_required
@kecamatan_required
def desa_delete(request, id):
    desa = get_object_or_404(Desa, id=id)

    if request.method == 'POST':
        desa.delete()
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'})

# ─────────────────────────────────────────
# DASHBOARD KECAMATAN
# ─────────────────────────────────────────

@login_required
@kecamatan_required
def dashboard_kecamatan(request):
    tahun_ini = datetime.date.today().year
    tahun     = int(request.GET.get('tahun', tahun_ini))
    desa_id   = request.GET.get('desa')

    # ── Base querysets per tahun ──
    qs_bumdes   = Bumdes.objects.filter(tahun_anggaran=tahun)
    qs_blt      = BLTDD.objects.filter(tahun_anggaran=tahun)
    qs_infra    = Infrastruktur.objects.filter(tahun_anggaran=tahun)
    qs_koperasi = Koperasi.objects.filter(tahun_anggaran=tahun)
    qs_pangan   = KetahananPangan.objects.filter(tahun_anggaran=tahun)

    # ── Stat Cards ──
    def agg(qs):
        return qs.aggregate(
            total     = Count('id'),
            pending   = Count('id', filter=Q(status='diajukan')),
            disetujui = Count('id', filter=Q(status='disetujui')),
            ditolak   = Count('id', filter=Q(status='ditolak')),
            draft     = Count('id', filter=Q(status='draft')),
        )

    stats = {
        'bumdes'  : agg(qs_bumdes),
        'blt'     : agg(qs_blt),
        'infra'   : agg(qs_infra),
        'koperasi': agg(qs_koperasi),
        'pangan'  : agg(qs_pangan),
    }

    total_pending_all = sum(s['pending']   for s in stats.values())
    total_disetujui   = sum(s['disetujui'] for s in stats.values())
    total_ditolak     = sum(s['ditolak']   for s in stats.values())
    total_draft       = sum(s['draft']     for s in stats.values())
    total_semua       = sum(s['total']     for s in stats.values())

    # ── Chart Bar: Sebaran per Desa (top 10) ──
    desa_qs = Desa.objects.annotate(
        jml_pengajuan=(
            Count('bumdes',          distinct=True) +
            Count('bltdd',           distinct=True) +
            Count('infrastruktur',   distinct=True) +
            Count('koperasi',        distinct=True) +
            Count('ketahananpangan', distinct=True)
        )
    ).order_by('-jml_pengajuan')[:10]

    # ── Semua Desa ──
    semua_desa = Desa.objects.all().order_by('nama')
    total_desa = semua_desa.count()

    # ── Tabel Rekap Status per Desa ──
    rekap_desa = []
    for desa in semua_desa:
        def status_desa(qs):
            obj = qs.filter(desa=desa).order_by('-created_at').first()
            return obj.status if obj else None

        bumdes_status   = status_desa(qs_bumdes)
        blt_status      = status_desa(qs_blt)
        infra_status    = status_desa(qs_infra)
        koperasi_status = status_desa(qs_koperasi)
        pangan_status   = status_desa(qs_pangan)

        sudah_lapor = any([bumdes_status, blt_status, infra_status, koperasi_status, pangan_status])

        rekap_desa.append({
            'desa'       : desa,
            'bumdes'     : bumdes_status,
            'blt'        : blt_status,
            'infra'      : infra_status,
            'koperasi'   : koperasi_status,
            'pangan'     : pangan_status,
            'sudah_lapor': sudah_lapor,
        })

    # ── Progress Kepatuhan per Modul + desa_list ──
    def hitung_kepatuhan(qs):
        desa_sudah_ids = set(qs.values_list('desa_id', flat=True).distinct())
        desa_lapor     = len(desa_sudah_ids)
        persen         = round((desa_lapor / total_desa) * 100) if total_desa else 0
        desa_list = sorted(
            [{'nama': d.nama, 'sudah': d.id in desa_sudah_ids} for d in semua_desa],
            key=lambda x: x['sudah']  # False (belum) duluan
        )
        return {
            'lapor'    : desa_lapor,
            'total'    : total_desa,
            'persen'   : persen,
            'desa_list': desa_list,
        }

    kepatuhan = {
        'bumdes'  : hitung_kepatuhan(qs_bumdes),
        'blt'     : hitung_kepatuhan(qs_blt),
        'infra'   : hitung_kepatuhan(qs_infra),
        'koperasi': hitung_kepatuhan(qs_koperasi),
        'pangan'  : hitung_kepatuhan(qs_pangan),
    }
    kepatuhan_render = [
        {'label': 'BUMDes',           **kepatuhan['bumdes']},
        {'label': 'BLT Dana Desa',    **kepatuhan['blt']},
        {'label': 'Infrastruktur',    **kepatuhan['infra']},
        {'label': 'Koperasi',         **kepatuhan['koperasi']},
        {'label': 'Ketahanan Pangan', **kepatuhan['pangan']},
    ]

    # ── Desa Belum Lapor Sama Sekali ──
    desa_sudah = set()
    for qs in [qs_bumdes, qs_blt, qs_infra, qs_koperasi, qs_pangan]:
        desa_sudah.update(qs.values_list('desa_id', flat=True))

    desa_belum_lapor = semua_desa.exclude(id__in=desa_sudah)

    # ── Daftar Tahun untuk Filter ──
    tahun_list = list(range(tahun_ini, tahun_ini - 5, -1))

    context = {
        'stats'            : stats,
        'total_pending_all': total_pending_all,
        'total_disetujui'  : total_disetujui,
        'total_ditolak'    : total_ditolak,
        'total_draft'      : total_draft,
        'total_semua'      : total_semua,
        'desa_labels'      : [d.nama for d in desa_qs],
        'desa_counts'      : [d.jml_pengajuan for d in desa_qs],
        'rekap_desa'       : rekap_desa,
        'kepatuhan'        : kepatuhan,
        'kepatuhan_render' : kepatuhan_render,
        'desa_belum_lapor' : desa_belum_lapor,
        'tahun_ini'        : tahun_ini,
        'tahun'            : tahun,
        'tahun_list'       : tahun_list,
        'total_desa'       : total_desa,
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