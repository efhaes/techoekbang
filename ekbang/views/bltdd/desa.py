from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from ekbang.models import BLTDD
from ekbang.forms.bltdd import BLTDDForm
from ekbang.views.auth import get_tahun_context
from ekbang.decorators import desa_required
import datetime


@login_required
@desa_required
def bltdd_list(request):
    desa             = request.user.profile.desa
    tahun, tahun_list = get_tahun_context(request)
    qs               = BLTDD.objects.filter(desa=desa, tahun_anggaran=tahun).order_by('-created_at')

    return render(request, 'desa/bltdd/list.html', {
        'bltdd_list': qs,
        'desa':       desa,
        'tahun':      tahun,
        'tahun_list': tahun_list,
        'form':       BLTDDForm(),
    })


@login_required
@desa_required
def bltdd_create(request):
    desa = request.user.profile.desa

    form = BLTDDForm(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        if form.is_valid():
            tahun_form = form.cleaned_data['tahun_anggaran']  # ← ambil dari cleaned_data

            existing = BLTDD.objects.filter(
                desa=desa,
                tahun_anggaran=tahun_form,
            ).exclude(status='ditolak').first()

            if existing:
                messages.warning(request, "Data BLT-DD tahun ini sudah ada. Silakan edit data yang ada.")
            else:
                obj               = form.save(commit=False)
                obj.desa          = desa
                obj.status        = 'draft'
                obj.save()
                messages.success(request, "Data BLT-DD berhasil disimpan sebagai draft.")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

    return redirect('bltdd_list')


@login_required
@desa_required
def bltdd_edit(request, pk):
    desa = request.user.profile.desa
    obj  = get_object_or_404(BLTDD, pk=pk, desa=desa)

    if obj.status not in ('draft', 'ditolak'):
        messages.error(request, "Data tidak bisa diedit karena sedang diproses atau sudah disetujui.")
        return redirect('bltdd_list')

    form = BLTDDForm(request.POST or None, request.FILES or None, instance=obj)

    if request.method == 'POST':
        if form.is_valid():
            edited               = form.save(commit=False)
            edited.tahun_anggaran = form.cleaned_data['tahun_anggaran']
            if edited.status == 'ditolak':
                edited.status = 'draft'
            edited.save()
            messages.success(request, "Data BLT-DD berhasil diperbarui.")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

    return redirect('bltdd_list')


@login_required
@desa_required
def bltdd_detail(request, pk):
    desa = request.user.profile.desa
    obj  = get_object_or_404(BLTDD, pk=pk, desa=desa)
    return render(request, 'desa/bltdd/detail.html', {'obj': obj})


@login_required
@desa_required
def bltdd_submit(request, pk):
    if request.method != 'POST':
        return redirect('bltdd_list')

    desa = request.user.profile.desa
    obj  = get_object_or_404(BLTDD, pk=pk, desa=desa)

    try:
        obj.ajukan(request.user)
        messages.success(request, "Data BLT-DD berhasil diajukan ke kecamatan.")
    except ValidationError as e:
        messages.error(request, str(e.message))

    return redirect('bltdd_list')


@login_required
@desa_required
def bltdd_delete(request, pk):
    if request.method != 'POST':
        return redirect('bltdd_list')

    desa = request.user.profile.desa
    obj  = get_object_or_404(BLTDD, pk=pk, desa=desa)

    if obj.status not in ('draft', 'ditolak'):
        messages.error(request, "Data tidak bisa dihapus karena sedang diproses atau sudah disetujui.")
        return redirect('bltdd_list')

    obj.delete()
    messages.success(request, "Data BLT-DD berhasil dihapus.")
    return redirect('bltdd_list')

