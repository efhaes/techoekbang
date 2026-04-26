from django import forms
from django.core.exceptions import ValidationError
from ekbang.models import BLTDD
import datetime


def tahun_choices():
    tahun_ini = datetime.date.today().year
    return [(y, str(y)) for y in range(2025, tahun_ini + 7)]


class BLTDDForm(forms.ModelForm):

    tahun_anggaran = forms.ChoiceField(
        choices=tahun_choices,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Tahun Anggaran',
    )

    class Meta:
        model  = BLTDD
        fields = [
            'tahun_anggaran',
            'nomor_sk',
            'jumlah_kpm',
            'nominal_per_bulan',
            'jumlah_bulan',
            'jumlah_total_terima',      # nama field yang benar
            'lpj_bulan_sebelumnya',     # nama field yang benar
            'file_sk',
            'file_surat_pengantar',
            'file_berita_acara',
        ]
        widgets = {
            'nomor_sk': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '001/SK/BLT/2025',
            }),
            'jumlah_kpm': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'min': '1',
            }),
            'nominal_per_bulan': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '300000',
                'min': '0',
            }),
            'jumlah_bulan': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'min': '1',
            }),
            'jumlah_total_terima': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Otomatis terhitung',
                'readonly': True,           # user tidak perlu isi manual
            }),
            'lpj_bulan_sebelumnya': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx',
            }),
            'file_sk': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx',
            }),
            'file_surat_pengantar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx',
            }),
            'file_berita_acara': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx',
            }),
        }
        labels = {
            'nomor_sk':            'Nomor SK',
            'jumlah_kpm':          'Jumlah KPM',
            'nominal_per_bulan':   'Nominal per Bulan (Rp)',
            'jumlah_total_terima': 'Jumlah Total Diterima (Rp)',
            'lpj_bulan_sebelumnya': 'LPJ Bulan Sebelumnya',
            'file_sk':             'File SK BLT',
            'file_surat_pengantar': 'Surat Pengantar',
            'file_berita_acara':   'Berita Acara',
        }

    def clean_tahun_anggaran(self):
        """ChoiceField return string, model butuh integer."""
        return int(self.cleaned_data['tahun_anggaran'])

    def clean(self):
        cleaned = super().clean()
        kpm     = cleaned.get('jumlah_kpm')
        nominal = cleaned.get('nominal_per_bulan')

        # Auto-hitung jumlah_total_terima = KPM × nominal × 12 bulan
        # Sesuaikan multiplier-nya jika BLT bukan 12 bulan
        if kpm and nominal:
            cleaned['jumlah_total_terima'] = kpm * nominal * 12

        return cleaned