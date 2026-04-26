from django import forms
from ekbang.models import Bumdes
import datetime


def tahun_choices():
    tahun_ini = datetime.date.today().year
    return [(y, str(y)) for y in range(2025, tahun_ini + 7)]


class BumdesForm(forms.ModelForm):

    tahun_anggaran = forms.ChoiceField(
        choices=tahun_choices,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Tahun Anggaran',
    )

    class Meta:
        model  = Bumdes
        fields = [
            'tahun_anggaran',
            'nama_bumdes', 'nomor_perdes', 'tanggal_perdes', 'nomor_sk',
            'file_sk',                          # tambahan — ada di model
            'direktur', 'komisaris', 'sekretaris', 'bendahara', 'ketua_unit_usaha',
            'ketua_pengawas', 'anggota_pengawas_1', 'anggota_pengawas_2',
            'file_surat_pengantar', 'file_berita_acara',
            # file_lpj DIHAPUS — tidak ada di model Bumdes
        ]
        widgets = {
            'nama_bumdes':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama BUMDes'}),
            'nomor_perdes':   forms.TextInput(attrs={'class': 'form-control', 'placeholder': '001/PERDES/2025'}),
            'tanggal_perdes': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'nomor_sk':       forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nomor SK'}),
            'file_sk':        forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx'}),

            # Pengurus
            'direktur':           forms.TextInput(attrs={'class': 'form-control'}),
            'komisaris':          forms.TextInput(attrs={'class': 'form-control'}),
            'sekretaris':         forms.TextInput(attrs={'class': 'form-control'}),
            'bendahara':          forms.TextInput(attrs={'class': 'form-control'}),
            'ketua_unit_usaha':   forms.TextInput(attrs={'class': 'form-control'}),

            # Pengawas
            'ketua_pengawas':     forms.TextInput(attrs={'class': 'form-control'}),
            'anggota_pengawas_1': forms.TextInput(attrs={'class': 'form-control'}),
            'anggota_pengawas_2': forms.TextInput(attrs={'class': 'form-control'}),

            # Dokumen
            'file_surat_pengantar': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx'}),
            'file_berita_acara':    forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx'}),
        }
        labels = {
            'nama_bumdes':    'Nama BUMDes',
            'nomor_perdes':   'Nomor Perdes',
            'tanggal_perdes': 'Tanggal Perdes',
            'nomor_sk':       'Nomor SK',
            'file_sk':        'File SK BUMDes',
            'direktur':       'Direktur',
            'komisaris':      'Komisaris',
            'sekretaris':     'Sekretaris',
            'bendahara':      'Bendahara',
            'ketua_unit_usaha':    'Ketua Unit Usaha',
            'ketua_pengawas':      'Ketua Pengawas',
            'anggota_pengawas_1':  'Anggota Pengawas 1',
            'anggota_pengawas_2':  'Anggota Pengawas 2',
            'file_surat_pengantar': 'Surat Pengantar',
            'file_berita_acara':    'Berita Acara',
        }

    def clean_tahun_anggaran(self):
        return int(self.cleaned_data['tahun_anggaran'])