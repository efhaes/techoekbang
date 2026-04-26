# ekbang/views/koperasi/desa.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from ekbang.models import Koperasi
from ekbang.forms.koprasi import KoperasiForm
from ekbang.decorators import desa_required
from ekbang.views.auth import get_tahun_context
import datetime


@login_required
@desa_required
def koperasi_list(request):
    # Pastikan fungsi ini mengembalikan desa, tahun, dan tahun_list yang benar
    desa = request.user.profile.desa
    tahun, tahun_list = get_tahun_context(request)

    qs = Koperasi.objects.filter(
        desa=desa,
        tahun_anggaran=tahun,
    ).order_by('-created_at')

    return render(request, 'desa/koperasi/list.html', {
        'object_list': qs,  # <--- WAJIB DIGANTI AGAR SINKRON DENGAN BASE
        'desa':        desa,
        'tahun':       tahun,
        'tahun_list':  tahun_list,
    })


@login_required
@desa_required
def koperasi_create(request):
    desa = request.user.profile.desa
    
    # AMBIL TAHUN DARI URL (?tahun=2025), kalau ga ada baru pake tahun sekarang
    tahun_target = request.GET.get('tahun', datetime.date.today().year)
    tahun_target = int(tahun_target) # Pastikan jadi angka

    # 1. CEK KUOTA (Cek tahun yang sedang dipilih/diklik user)
    jumlah_koperasi = Koperasi.objects.filter(
        desa=desa, 
        tahun_anggaran=tahun_target # <--- Sekarang ceknya tahun yang diklik
    ).exclude(status='ditolak').count()

    # Limit (Misal 1 atau 2 sesuai kebutuhanmu)
    if jumlah_koperasi >= 1: 
        messages.error(request, f"Maaf, data Koperasi tahun {tahun_target} sudah ada.")
        return redirect('koperasi_list')

    # Isi Form otomatis dengan tahun yang dipilih (initial)
    form = KoperasiForm(request.POST or None, request.FILES or None, initial={'tahun_anggaran': tahun_target})
    
    if request.method == 'POST':
        if form.is_valid():
            tahun_form = form.cleaned_data.get('tahun_anggaran')
            
            # Double check di database
            existing = Koperasi.objects.filter(
                desa=desa,
                tahun_anggaran=tahun_form,
            ).exclude(status='ditolak').exists()

            if existing:
                messages.warning(request, f"Data koperasi untuk tahun {tahun_form} sudah ada.")
                return render(request, 'desa/koperasi/form.html', {'form': form})

            obj = form.save(commit=False)
            obj.desa = desa
            obj.save()
            messages.success(request, "Data berhasil disimpan.")
            return redirect('koperasi_list')

    return render(request, 'desa/koperasi/form.html', {
        'form': form,
        'title': f'Tambah Koperasi Tahun {tahun_target}',
        'is_edit': False,
    })


@login_required
@desa_required
def koperasi_edit(request, pk):
    desa = request.user.profile.desa
    obj  = get_object_or_404(Koperasi, pk=pk, desa=desa)

    if obj.status not in ('draft', 'ditolak'):
        messages.error(request, "Data tidak bisa diedit karena sedang diproses atau sudah disetujui.")
        return redirect('koperasi_list')

    form = KoperasiForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        edited = form.save(commit=False)
        if edited.status == 'ditolak':
            edited.status = 'draft'
        edited.save()
        messages.success(request, "Data koperasi berhasil diperbarui.")
        return redirect('koperasi_list')

    return render(request, 'desa/koperasi/form.html', {
        'form':    form,
        'obj':     obj,
        'title':   'Edit Koperasi',
        'is_edit': True,
    })


@login_required
@desa_required
def koperasi_detail(request, pk):
    desa = request.user.profile.desa
    obj  = get_object_or_404(Koperasi, pk=pk, desa=desa)
    return render(request, 'desa/koperasi/detail.html', {'obj': obj})


@login_required
@desa_required
def koperasi_submit(request, pk):
    if request.method != 'POST':
        return redirect('koperasi_list')

    desa = request.user.profile.desa
    obj  = get_object_or_404(Koperasi, pk=pk, desa=desa)

    try:
        obj.ajukan(request.user)
        messages.success(request, "Data koperasi berhasil diajukan ke kecamatan.")
    except ValidationError as e:
        messages.error(request, str(e.message))

    return redirect('koperasi_list')


@login_required
@desa_required
def koperasi_delete(request, pk):
    if request.method != 'POST':
        return redirect('koperasi_list')

    desa = request.user.profile.desa
    obj  = get_object_or_404(Koperasi, pk=pk, desa=desa)

    if obj.status not in ('draft', 'ditolak'):
        messages.error(request, "Data tidak bisa dihapus karena sedang diproses atau sudah disetujui.")
        return redirect('koperasi_list')

    obj.delete()
    messages.success(request, "Data koperasi berhasil dihapus.")
    return redirect('koperasi_list')