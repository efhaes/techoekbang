# ekbang/views/ketahanan/kecamatan.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Count, Q
from ekbang.models import KetahananPangan, Desa              # tambah Desa
from ekbang.decorators import kecamatan_required
from ekbang.views.auth import get_tahun_context


@login_required
@kecamatan_required
def ketahanan_pangan_list_kecamatan(request):
    status_filter     = request.GET.get('status', '')
    desa_filter       = request.GET.get('desa', '')          # tambah
    tahun, tahun_list = get_tahun_context(request)

    return render(request, 'kecamatan/ketahanan_pangan/list.html', {
        'status_filter':  status_filter,
        'desa_filter':    desa_filter,                       # tambah
        'desa_list':      Desa.objects.all(),                # tambah
        'tahun':          tahun,
        'tahun_list':     tahun_list,
    })


@login_required
@kecamatan_required
def ketahanan_pangan_filter_api(request):
    tahun = request.GET.get('tahun')
    desa_id = request.GET.get('desa_id')
    status_filter = request.GET.get('status', '')

    if not tahun or not desa_id:
        return JsonResponse({'error': 'Parameter tahun dan desa_id wajib diisi'}, status=400)

    qs = KetahananPangan.objects.select_related('desa', 'diajukan_oleh').filter(
        tahun_anggaran=tahun,
        desa_id=desa_id
    ).exclude(status='draft').order_by('-tanggal_diajukan')

    if status_filter in ('diajukan', 'disetujui', 'ditolak'):
        qs = qs.filter(status=status_filter)

    summary = KetahananPangan.objects.filter(
        tahun_anggaran=tahun, desa_id=desa_id
    ).exclude(status='draft').aggregate(
        total_diajukan=Count('id', filter=Q(status='diajukan')),
        total_disetujui=Count('id', filter=Q(status='disetujui')),
        total_ditolak=Count('id', filter=Q(status='ditolak')),
    )

    data = []
    for obj in qs:
        data.append({
            'pk': obj.pk,
            'desa_nama': obj.desa.nama,
            'nama_kelompok': obj.nama_kelompok,
            'tanggal_diajukan': obj.tanggal_diajukan.strftime('%d %b %Y') if obj.tanggal_diajukan else '-',
            'status': obj.status,
            'status_display': obj.get_status_display()
        })

    # Debug info
    print(f"DEBUG KETAHANAN PANGAN: tahun={tahun}, desa_id={desa_id}, status_filter={status_filter}")
    print(f"DEBUG KETAHANAN PANGAN: qs.count()={qs.count()}")
    print(f"DEBUG KETAHANAN PANGAN: summary={summary}")
    print(f"DEBUG KETAHANAN PANGAN: data length={len(data)}")

    return JsonResponse({
        'data': data,
        'summary': summary
    })


@login_required
@kecamatan_required
def ketahanan_pangan_detail_kecamatan(request, pk):
    obj = get_object_or_404(
        KetahananPangan.objects.select_related(
            'desa', 'diajukan_oleh', 'diverifikasi_oleh'
        ),
        pk=pk,
    )
    if obj.status == 'draft':
        messages.error(request, "Data belum diajukan oleh desa.")
        return redirect('ketahanan_pangan_list_kecamatan')
    return render(request, 'kecamatan/ketahanan_pangan/detail.html', {'obj': obj})


@login_required
@kecamatan_required
def ketahanan_pangan_verifikasi(request, pk):
    if request.method != 'POST':
        return redirect('ketahanan_pangan_detail_kecamatan', pk=pk)

    obj     = get_object_or_404(KetahananPangan, pk=pk)
    status  = request.POST.get('status', '').strip()
    catatan = request.POST.get('catatan_verifikasi', '').strip()

    if status not in ('disetujui', 'ditolak'):
        messages.error(request, "Status verifikasi tidak valid.")
        return redirect('ketahanan_pangan_detail_kecamatan', pk=pk)

    if status == 'ditolak' and not catatan:
        messages.error(request, "Alasan penolakan wajib diisi.")
        return redirect('ketahanan_pangan_detail_kecamatan', pk=pk)

    try:
        obj.verifikasi(request.user, status, catatan)
        if status == 'disetujui':
            messages.success(request, f"Ketahanan Pangan {obj.nama_kelompok} Desa {obj.desa.nama} telah disetujui.")
        else:
            messages.warning(request, f"Ketahanan Pangan {obj.nama_kelompok} Desa {obj.desa.nama} telah ditolak.")
    except ValidationError as e:
        messages.error(request, str(e.message))

    return redirect('ketahanan_pangan_list_kecamatan')