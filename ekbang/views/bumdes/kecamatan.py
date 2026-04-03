# ekbang/views/bumdes/kecamatan.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Count, Q
from ekbang.models import Bumdes, Desa
from ekbang.decorators import kecamatan_required
from ekbang.views.auth import get_tahun_context


@login_required
@kecamatan_required
def bumdes_list_kecamatan(request):
    status_filter     = request.GET.get('status', '')
    desa_filter       = request.GET.get('desa', '')
    tahun, tahun_list = get_tahun_context(request)

    return render(request, 'kecamatan/bumdes/list.html', {
        'status_filter': status_filter,
        'desa_filter':   desa_filter,
        'desa_list':     Desa.objects.all(),
        'tahun':         tahun,
        'tahun_list':    tahun_list,
    })


@login_required
@kecamatan_required
def bumdes_filter_api(request):
    tahun = request.GET.get('tahun')
    desa_id = request.GET.get('desa_id')
    status_filter = request.GET.get('status', '')

    if not tahun or not desa_id:
        return JsonResponse({'error': 'Parameter tahun dan desa_id wajib diisi'}, status=400)

    qs = Bumdes.objects.select_related('desa').filter(
        tahun_anggaran=tahun,
        desa_id=desa_id
    ).exclude(status='draft').order_by('-tanggal_diajukan')

    if status_filter in ('diajukan', 'disetujui', 'ditolak'):
        qs = qs.filter(status=status_filter)

    summary = Bumdes.objects.filter(tahun_anggaran=tahun, desa_id=desa_id).exclude(status='draft').aggregate(
        total_diajukan=Count('id', filter=Q(status='diajukan')),
        total_disetujui=Count('id', filter=Q(status='disetujui')),
        total_ditolak=Count('id', filter=Q(status='ditolak')),
    )

    data = []
    for obj in qs:
        data.append({
            'pk': obj.pk,
            'desa_nama': obj.desa.nama,
            'nama_bumdes': obj.nama_bumdes,
            'nomor_sk': obj.nomor_sk or '-',
            'tanggal_diajukan': obj.tanggal_diajukan.strftime('%d %b %Y') if obj.tanggal_diajukan else '-',
            'status': obj.status,
            'status_display': obj.get_status_display()
        })

    # Debug info
    print(f"DEBUG BUMDES: tahun={tahun}, desa_id={desa_id}, status_filter={status_filter}")
    print(f"DEBUG BUMDES: qs.count()={qs.count()}")
    print(f"DEBUG BUMDES: summary={summary}")
    print(f"DEBUG BUMDES: data length={len(data)}")

    return JsonResponse({
        'data': data,
        'summary': summary
    })


@login_required
@kecamatan_required
def bumdes_detail_kecamatan(request, pk):
    bumdes = get_object_or_404(
        Bumdes.objects.select_related('desa', 'diajukan_oleh', 'diverifikasi_oleh'),
        pk=pk,
    )
    if bumdes.status == 'draft':
        messages.error(request, "Data belum diajukan oleh desa.")
        return redirect('bumdes_list_kecamatan')
    return render(request, 'kecamatan/bumdes/detail.html', {'bumdes': bumdes})


@login_required
@kecamatan_required
def bumdes_verifikasi(request, pk):
    if request.method != 'POST':
        return redirect('bumdes_detail_kecamatan', pk=pk)

    bumdes  = get_object_or_404(Bumdes, pk=pk)
    status  = request.POST.get('status', '').strip()
    catatan = request.POST.get('catatan_verifikasi', '').strip()

    if status not in ('disetujui', 'ditolak'):
        messages.error(request, "Status verifikasi tidak valid.")
        return redirect('bumdes_detail_kecamatan', pk=pk)

    if status == 'ditolak' and not catatan:
        messages.error(request, "Alasan penolakan wajib diisi.")
        return redirect('bumdes_detail_kecamatan', pk=pk)

    try:
        bumdes.verifikasi(request.user, status, catatan)
        if status == 'disetujui':
            messages.success(request, f"BUMDes {bumdes.nama_bumdes} dari Desa {bumdes.desa.nama} telah disetujui.")
        else:
            messages.warning(request, f"BUMDes {bumdes.nama_bumdes} dari Desa {bumdes.desa.nama} telah ditolak.")
    except ValidationError as e:
        messages.error(request, str(e.message))

    return redirect('bumdes_list_kecamatan')