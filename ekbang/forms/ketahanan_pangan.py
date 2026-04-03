from django import forms
from ekbang.models import KetahananPangan
import datetime


def tahun_choices():
    tahun_ini = datetime.date.today().year
    return [(y, str(y)) for y in range(2025, tahun_ini + 7)]


class KetahananPanganForm(forms.ModelForm):

    tahun_anggaran = forms.ChoiceField(
        choices=tahun_choices,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Tahun Anggaran',
    )

    class Meta:
        model = KetahananPangan
        fields = [
        'tahun_anggaran',
        'nama_kelompok',
        'nomor_sk',
        'tanggal_sk',
        'pembiayaan_anggaran',
        'ketua',
        'usaha_pertanian',
        'usaha_peternakan',
        'usaha_perladangan',
        'usaha_perdagangan',
        'usaha_perikanan',
        'usaha_lainnya',
        'proposal',          # ← tambah ini
        'file_lpj_ketahanan', # ← tambah ini
        'file_surat_pengantar',
        'file_berita_acara',
        'file_sk',            # ← tambah ini
    ]

        widgets = {
            'nama_kelompok': forms.TextInput(attrs={'class': 'form-control'}),
            'nomor_sk': forms.TextInput(attrs={'class': 'form-control'}),
            'tanggal_sk': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'pembiayaan_anggaran': forms.NumberInput(attrs={'class': 'form-control'}),
            'ketua': forms.TextInput(attrs={'class': 'form-control'}),

            # checkbox
            'usaha_pertanian': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'usaha_peternakan': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'usaha_perladangan': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'usaha_perdagangan': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'usaha_perikanan': forms.CheckboxInput(attrs={'class': 'form-check-input'}),

            'usaha_lainnya': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Isi jika tidak ada di pilihan...'
            }),
            'proposal':            forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx'}),
        'file_lpj_ketahanan':  forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx'}),
        'file_surat_pengantar': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx'}),
        'file_berita_acara':    forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx'}),
        'file_sk':              forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx'}),
    
        }

    def clean_tahun_anggaran(self):
        return int(self.cleaned_data['tahun_anggaran'])