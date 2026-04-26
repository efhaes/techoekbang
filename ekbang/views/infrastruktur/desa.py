# ekbang/views/infrastruktur/desa.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.urls import reverse

from ekbang.models import Infrastruktur
from ekbang.forms.infrastruktur import (
    InfrastrukturForm,
    InfrastrukturDetailFormSet,
    InfrastrukturFotoFormSet
)

from ekbang.decorators import desa_required
from ekbang.views.auth import get_tahun_context


# ─────────────────────────────────────────
# LIST
# ─────────────────────────────────────────
@login_required
@desa_required
def infrastruktur_list(request):
    desa, tahun, tahun_list = _get_context_desa_tahun(request)

    qs = Infrastruktur.objects.filter(
        desa=desa,
        tahun_anggaran=tahun
    ).order_by('-created_at')

    return render(request, 'desa/infrastruktur/list.html', {
        'object_list': qs,  # <--- UBAH INI dari 'infrastruktur_list' ke 'object_list'
        'desa': desa,
        'tahun': tahun,
        'tahun_list': tahun_list,
        'title': 'Data Infrastruktur' # Tambahkan ini jika belum ada
    })


# ─────────────────────────────────────────
# CREATE
# ─────────────────────────────────────────
@login_required
@desa_required
def infrastruktur_create(request):
    desa = request.user.profile.desa

    form = InfrastrukturForm(request.POST or None, request.FILES or None)
    formset_detail = InfrastrukturDetailFormSet(request.POST or None)
    formset_foto   = InfrastrukturFotoFormSet(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        if form.is_valid() and formset_detail.is_valid() and formset_foto.is_valid():
            
            tahun_dipilih = form.cleaned_data.get('tahun_anggaran')
            # Sesuaikan dengan nama field di model kamu: 'kegiatan'
            nama_kegiatan = form.cleaned_data.get('kegiatan') 

            # Cek duplikat: Desa + Tahun + Nama Kegiatan
            existing = Infrastruktur.objects.filter(
                desa=desa,
                tahun_anggaran=tahun_dipilih,
                kegiatan__iexact=nama_kegiatan 
            ).exclude(status='ditolak').exists()

            if existing:
                messages.warning(request, f"Kegiatan '{nama_kegiatan}' tahun {tahun_dipilih} sudah pernah diinput.")
                return render(request, 'desa/infrastruktur/form.html', {
                    'form': form,
                    'formset': formset_detail,
                    'formset_foto': formset_foto,
                    'title': 'Tambah Infrastruktur',
                    'is_edit': False,
                })

            # Simpan jika aman
            obj = form.save(commit=False)
            obj.desa = desa
            obj.status = 'draft'
            obj.save()

            formset_detail.instance = obj
            formset_detail.save()

            formset_foto.instance = obj
            formset_foto.save()

            messages.success(request, f"Data {nama_kegiatan} berhasil disimpan sebagai draft.")
            # Pastikan fungsi redirect_with_tahun ini sudah kamu buat ya
            return redirect_with_tahun(obj.tahun_anggaran) 
        
        else:
            messages.error(request, "Terjadi kesalahan. Mohon periksa kembali isian Form dan Foto.")

    return render(request, 'desa/infrastruktur/form.html', {
        'form': form,
        'formset': formset_detail,
        'formset_foto': formset_foto,
        'title': 'Tambah Infrastruktur',
        'is_edit': False,
    })

# ─────────────────────────────────────────
# EDIT
# ─────────────────────────────────────────
@login_required
@desa_required
def infrastruktur_edit(request, pk):
    desa = request.user.profile.desa
    obj  = get_object_or_404(Infrastruktur, pk=pk, desa=desa)

    if obj.status not in ('draft', 'ditolak'):
        messages.error(request, "Data tidak bisa diedit.")
        return redirect_with_tahun(obj.tahun_anggaran)

    form = InfrastrukturForm(request.POST or None, request.FILES or None, instance=obj)

    formset_detail = InfrastrukturDetailFormSet(
        request.POST or None,
        request.FILES or None,
        instance=obj,
        # ← hapus prefix='detail'
    )

    formset_foto = InfrastrukturFotoFormSet(
        request.POST or None,
        request.FILES or None,
        instance=obj,
        # ← hapus prefix='foto'
    )

    if request.method == 'POST':
        if form.is_valid() and formset_detail.is_valid() and formset_foto.is_valid():

            edited = form.save(commit=False)

            if edited.status == 'ditolak':
                edited.status = 'draft'

            edited.save()

            formset_detail.instance = obj
            formset_detail.save()

            formset_foto.instance = obj
            formset_foto.save()

            messages.success(request, "Berhasil update.")
            return redirect_with_tahun(edited.tahun_anggaran)

        else:
            print(form.errors)
            print(formset_detail.errors)
            print(formset_foto.errors)

    return render(request, 'desa/infrastruktur/form.html', {
        'form': form,
        'formset': formset_detail,
        'formset_foto': formset_foto,
        'obj': obj,
        'title': 'Edit Infrastruktur',
        'is_edit': True,
    })


@login_required
@desa_required
def infrastruktur_detail(request, pk):
    desa = request.user.profile.desa

    obj = get_object_or_404(
        Infrastruktur.objects.prefetch_related('details', 'fotos'),
        pk=pk,
        desa=desa
    )

    return render(request, 'desa/infrastruktur/detail.html', {
        'infra': obj  # ← sebelumnya 'obj': obj
    })

# ─────────────────────────────────────────
# SUBMIT
# ─────────────────────────────────────────
@login_required
@desa_required
def infrastruktur_submit(request, pk):
    if request.method != 'POST':
        return redirect('infrastruktur_list')

    desa = request.user.profile.desa
    obj  = get_object_or_404(Infrastruktur, pk=pk, desa=desa)

    try:
        obj.ajukan(request.user)
        messages.success(request, "Data berhasil diajukan ke kecamatan.")
    except ValidationError as e:
        messages.error(request, str(e))

    return redirect_with_tahun(obj.tahun_anggaran)


# ─────────────────────────────────────────
# DELETE
# ─────────────────────────────────────────
@login_required
@desa_required
def infrastruktur_delete(request, pk):
    if request.method != 'POST':
        return redirect('infrastruktur_list')

    desa = request.user.profile.desa
    obj  = get_object_or_404(Infrastruktur, pk=pk, desa=desa)

    if obj.status not in ('draft', 'ditolak'):
        messages.error(request, "Data tidak bisa dihapus.")
        return redirect_with_tahun(obj.tahun_anggaran)

    tahun = obj.tahun_anggaran
    obj.delete()

    messages.success(request, "Data berhasil dihapus.")

    return redirect_with_tahun(tahun)


# ─────────────────────────────────────────
# HELPERS (BIAR CLEAN)
# ─────────────────────────────────────────

def _get_context_desa_tahun(request):
    desa = request.user.profile.desa
    tahun, tahun_list = get_tahun_context(request)
    return desa, tahun, tahun_list


def redirect_with_tahun(tahun):
    return redirect(reverse('infrastruktur_list') + f'?tahun={tahun}')