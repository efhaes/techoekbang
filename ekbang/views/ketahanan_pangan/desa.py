# ekbang/views/ketahanan/desa.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from ekbang.models import KetahananPangan
from ekbang.forms.ketahanan_pangan import KetahananPanganForm
from ekbang.decorators import desa_required
from ekbang.views.auth import get_tahun_context


@login_required
@desa_required
def ketahanan_pangan_list(request):
    desa              = request.user.profile.desa
    tahun, tahun_list = get_tahun_context(request)

    qs = KetahananPangan.objects.filter(
        desa=desa,
        tahun_anggaran=tahun,
    ).order_by('-created_at')

    return render(request, 'desa/ketahanan_pangan/list.html', {
        'ketahanan_list': qs,
        'object_list': qs,
        'desa':           desa,
        'tahun':          tahun,
        'tahun_list':     tahun_list,
    })


@login_required
@desa_required
def ketahanan_pangan_create(request):
    desa = request.user.profile.desa
    form = KetahananPanganForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        obj        = form.save(commit=False)
        obj.desa   = desa
        obj.status = 'draft'
        obj.save()
        # hapus form.save_m2m() — sudah tidak pakai M2M
        messages.success(request, "Data ketahanan pangan berhasil disimpan sebagai draft.")
        return redirect('ketahanan_pangan_list')

    return render(request, 'desa/ketahanan_pangan/form.html', {
        'form':    form,
        'title':   'Tambah Ketahanan Pangan',
        'is_edit': False,
    })


@login_required
@desa_required
def ketahanan_pangan_edit(request, pk):
    desa = request.user.profile.desa
    obj  = get_object_or_404(KetahananPangan, pk=pk, desa=desa)

    if obj.status not in ('draft', 'ditolak'):
        messages.error(request, "Data tidak bisa diedit karena sedang diproses atau sudah disetujui.")
        return redirect('ketahanan_pangan_list')

    form = KetahananPanganForm(request.POST or None, request.FILES or None, instance=obj)

    if request.method == 'POST' and form.is_valid():
        edited = form.save(commit=False)
        if edited.status == 'ditolak':
            edited.status = 'draft'
        edited.save()
        # hapus form.save_m2m() — sudah tidak pakai M2M
        messages.success(request, "Data ketahanan pangan berhasil diperbarui.")
        return redirect('ketahanan_pangan_list')

    return render(request, 'desa/ketahanan_pangan/form.html', {
        'form':    form,
        'obj':     obj,
        'title':   'Edit Ketahanan Pangan',
        'is_edit': True,
    })


@login_required
@desa_required
def ketahanan_pangan_detail(request, pk):
    desa = request.user.profile.desa
    obj  = get_object_or_404(
        KetahananPangan,  # hapus prefetch_related — sudah tidak pakai M2M
        pk=pk, desa=desa,
    )
    return render(request, 'desa/ketahanan_pangan/detail.html', {'obj': obj})


@login_required
@desa_required
def ketahanan_pangan_submit(request, pk):
    if request.method != 'POST':
        return redirect('ketahanan_pangan_list')

    desa = request.user.profile.desa
    obj  = get_object_or_404(KetahananPangan, pk=pk, desa=desa)

    try:
        obj.ajukan(request.user)
        messages.success(request, "Data ketahanan pangan berhasil diajukan ke kecamatan.")
    except ValidationError as e:
        messages.error(request, str(e.message))

    return redirect('ketahanan_pangan_list')


@login_required
@desa_required
def ketahanan_pangan_delete(request, pk):
    if request.method != 'POST':
        return redirect('ketahanan_pangan_list')

    desa = request.user.profile.desa
    obj  = get_object_or_404(KetahananPangan, pk=pk, desa=desa)

    if obj.status not in ('draft', 'ditolak'):
        messages.error(request, "Data tidak bisa dihapus karena sedang diproses atau sudah disetujui.")
        return redirect('ketahanan_pangan_list')

    obj.delete()
    messages.success(request, "Data ketahanan pangan berhasil dihapus.")
    return redirect('ketahanan_pangan_list')