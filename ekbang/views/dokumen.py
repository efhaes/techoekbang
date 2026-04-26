import os
from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from ekbang.views import desa_required

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates_dokumen')

TEMPLATE_LIST = [
    {
        'id': 'surat_pengantar',
        'nama': 'Surat Pengantar',
        'deskripsi': 'Surat pengantar permohonan pencairan Bantuan Keuangan kepada DPM-DESA Prov. Jawa Barat melalui DPMD Kab. Bogor',
        'icon': '📄',
        'file': 'FORMAT_SURAT_PENGANTAR_DAN_BA_VERIFIKASI_BANKEUPROV_2025.docx',
    },
    {
        'id': 'berita_acara',
        'nama': 'Berita Acara Verifikasi Penyaluran',
        'deskripsi': 'Berita acara verifikasi persyaratan administrasi permohonan penyaluran Bantuan Keuangan Desa Tahun 2025',
        'icon': '📋',
        'file': 'FORMAT_SURAT_PENGANTAR_DAN_BA_VERIFIKASI_BANKEUPROV_2025.docx',
    },
    {
        'id': 'lpj',
        'nama': 'Berita Acara LPJ',
        'deskripsi': 'Berita acara verifikasi dokumen Laporan Pertanggungjawaban Bantuan Keuangan Desa Tahun 2024',
        'icon': '📊',
        'file': 'FORMAT_SURAT_PENGANTAR_DAN_BA_VERIFIKASI_BANKEUPROV_2025.docx',
    },
]


@login_required
@desa_required
def template_dokumen(request):
    return render(request, 'desa/template_dokumen.html', {
        'template_list': TEMPLATE_LIST
    })


@login_required
@desa_required
def download_template(request, jenis):
    template = next((t for t in TEMPLATE_LIST if t['id'] == jenis), None)
    if not template:
        raise Http404

    file_path = os.path.join(TEMPLATE_DIR, template['file'])
    if not os.path.exists(file_path):
        raise Http404("File template tidak ditemukan.")

    with open(file_path, 'rb') as f:
        content = f.read()

    response = HttpResponse(
        content,
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
    response['Content-Disposition'] = f'attachment; filename="{template["file"]}"'
    return response