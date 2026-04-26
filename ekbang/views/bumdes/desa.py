from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from ekbang.models import Bumdes
from ekbang.forms.bumdes import BumdesForm
from ekbang.decorators import desa_required   # lebih rapi di file tersendiri
import datetime


@login_required
@desa_required
def bumdes_list(request):
    desa     = request.user.profile.desa
    tahun_ini = datetime.date.today().year

    try:
        tahun = int(request.GET.get('tahun', tahun_ini))
    except (ValueError, TypeError):
        tahun = tahun_ini

    bumdes_qs = Bumdes.objects.filter(
        desa=desa,
        tahun_anggaran=tahun,
    ).order_by('-created_at')

    return render(request, 'desa/bumdes/list.html', {
        'bumdes_list': bumdes_qs,
        'desa':        desa,
        'tahun':       tahun,
        'tahun_list':  list(range(2025, tahun_ini + 5)),
    })


@login_required
@desa_required
def bumdes_create(request):
    desa = request.user.profile.desa
    tahun_target = int(request.GET.get('tahun', datetime.date.today().year))

    # Cek Kuota (Maks 3 Unit)
    jumlah = Bumdes.objects.filter(
        desa=desa, tahun_anggaran=tahun_target
    ).exclude(status='ditolak').count()

    if jumlah >= 5:
        messages.error(request, f"Jatah input BUMDes tahun {tahun_target} sudah maksimal 5.")
        return redirect('bumdes_list')

    form = BumdesForm(request.POST or None, request.FILES or None, initial={'tahun_anggaran': tahun_target})

    if request.method == 'POST' and form.is_valid():
        nama = form.cleaned_data.get('nama_bumdes')
        # Cek Duplikasi Nama di Tahun yang Sama
        if Bumdes.objects.filter(desa=desa, tahun_anggaran=tahun_target, nama_bumdes__iexact=nama).exists():
            messages.warning(request, f"BUMDes '{nama}' sudah terdaftar di tahun {tahun_target}.")
        else:
            obj = form.save(commit=False)
            obj.desa = desa
            obj.status = 'draft'
            obj.save()
            messages.success(request, f"BUMDes {nama} berhasil disimpan.")
            return redirect('bumdes_list')

    return render(request, 'desa/bumdes/form.html', {
        'form': form, 'title': f'Tambah BUMDes Tahun {tahun_target}', 'is_edit': False
    })


@login_required
@desa_required
def bumdes_edit(request, pk):
    desa   = request.user.profile.desa
    bumdes = get_object_or_404(Bumdes, pk=pk, desa=desa)

    if bumdes.status not in ('draft', 'ditolak'):
        messages.error(request, "Data tidak bisa diedit.")
        return redirect('bumdes_list')

    form = BumdesForm(request.POST or None, request.FILES or None, instance=bumdes)

    if request.method == 'POST':
        if form.is_valid():
            obj = form.save(commit=False)
            if obj.status == 'ditolak':
                obj.status = 'draft'
            obj.save()
            messages.success(request, "Data BUMDes berhasil diperbarui.")
            return redirect('bumdes_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            return redirect('bumdes_list')

    return render(request, 'desa/bumdes/form.html', {
        'form':    form,
        'bumdes':  bumdes,
        'title':   'Edit Data BUMDes',
        'is_edit': True,
    })


@login_required
@desa_required
def bumdes_detail(request, pk):
    desa   = request.user.profile.desa
    bumdes = get_object_or_404(Bumdes, pk=pk, desa=desa)
    return render(request, 'desa/bumdes/detail.html', {'bumdes': bumdes})


@login_required
@desa_required
def bumdes_submit(request, pk):
    if request.method != 'POST':
        return redirect('bumdes_list')

    desa   = request.user.profile.desa
    bumdes = get_object_or_404(Bumdes, pk=pk, desa=desa)

    try:
        # Pakai method ajukan() dari model — tidak duplikasi logika
        bumdes.ajukan(request.user)
        messages.success(request, "Data BUMDes berhasil diajukan ke kecamatan.")
    except ValidationError as e:
        messages.error(request, str(e.message))

    return redirect('bumdes_list')


@login_required
@desa_required
def bumdes_delete(request, pk):
    if request.method != 'POST':
        return redirect('bumdes_list')

    desa   = request.user.profile.desa
    bumdes = get_object_or_404(Bumdes, pk=pk, desa=desa)

    if bumdes.status not in ('draft', 'ditolak'):
        messages.error(request, "Data tidak bisa dihapus karena sedang diproses atau sudah disetujui.")
        return redirect('bumdes_list')

    bumdes.delete()
    messages.success(request, "Data BUMDes berhasil dihapus.")
    return redirect('bumdes_list')