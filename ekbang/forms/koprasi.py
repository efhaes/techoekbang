from django import forms
from ekbang.models import Koperasi
import datetime


def tahun_choices():
    tahun_ini = datetime.date.today().year
    return [(y, str(y)) for y in range(2025, tahun_ini + 7)]


class KoperasiForm(forms.ModelForm):

    tahun_anggaran = forms.ChoiceField(
        choices=tahun_choices,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Tahun Anggaran',
    )

    class Meta:
        model  = Koperasi
        fields = [
            'tahun_anggaran',
            'nama_koperasi',
            'nomor_sk',
            'tanggal_sk',           # bukan tanggal_musyawarah
            'akta_notaris_nomor',   # ada di model, tidak diinclude
            'ketua',
            'wakil_bidang_anggota',
            'wakil_bidang_usaha',
            'sekretaris',
            'bendahara',
            'ketua_pengawas',
            'anggota_pengawas_1',
            'anggota_pengawas_2',
            'file_sk',              # ada di model, tidak diinclude
            'file_rapbk',           # ada di model, tidak diinclude
            'file_surat_pengantar',
            'file_berita_acara',
            # file_lpj DIHAPUS — tidak ada di model Koperasi
        ]
        widgets = {
            'nama_koperasi':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama Koperasi'}),
            'nomor_sk':           forms.TextInput(attrs={'class': 'form-control', 'placeholder': '001/SK/2025'}),
            'tanggal_sk':         forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'akta_notaris_nomor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nomor akta notaris'}),

            # Pengurus
            'ketua':                forms.TextInput(attrs={'class': 'form-control'}),
            'wakil_bidang_anggota': forms.TextInput(attrs={'class': 'form-control'}),
            'wakil_bidang_usaha':   forms.TextInput(attrs={'class': 'form-control'}),
            'sekretaris':           forms.TextInput(attrs={'class': 'form-control'}),
            'bendahara':            forms.TextInput(attrs={'class': 'form-control'}),

            # Pengawas
            'ketua_pengawas':     forms.TextInput(attrs={'class': 'form-control'}),
            'anggota_pengawas_1': forms.TextInput(attrs={'class': 'form-control'}),
            'anggota_pengawas_2': forms.TextInput(attrs={'class': 'form-control'}),

            # Dokumen
            'file_sk':    forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx'}),
            'file_rapbk': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx'}),
            'file_surat_pengantar': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx'}),
            'file_berita_acara':    forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx'}),
        }
        labels = {
            'nama_koperasi':      'Nama Koperasi',
            'nomor_sk':           'Nomor SK',
            'tanggal_sk':         'Tanggal SK',
            'akta_notaris_nomor': 'Nomor Akta Notaris',
            'ketua':                'Ketua',
            'wakil_bidang_anggota': 'Wakil Bidang Anggota',
            'wakil_bidang_usaha':   'Wakil Bidang Usaha',
            'sekretaris':           'Sekretaris',
            'bendahara':            'Bendahara',
            'ketua_pengawas':     'Ketua Pengawas',
            'anggota_pengawas_1': 'Anggota Pengawas 1',
            'anggota_pengawas_2': 'Anggota Pengawas 2',
            'file_sk':    'File SK',
            'file_rapbk': 'File RAPBK',
            'file_surat_pengantar': 'Surat Pengantar',
            'file_berita_acara':    'Berita Acara',
        }

    def clean_tahun_anggaran(self):
        return int(self.cleaned_data['tahun_anggaran'])