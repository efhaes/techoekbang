from django import forms
from django.forms import inlineformset_factory
from ekbang.models import Infrastruktur, InfrastrukturDetail,InfrastrukturFoto
import datetime


def tahun_choices():
    tahun_ini = datetime.date.today().year
    return [(y, str(y)) for y in range(2025, tahun_ini + 7)]


# ──────────────────────────────────────────
# Form utama Infrastruktur
# ──────────────────────────────────────────

class InfrastrukturForm(forms.ModelForm):

    tahun_anggaran = forms.ChoiceField(
        choices=tahun_choices,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Tahun Anggaran',
    )

    class Meta:
        model  = Infrastruktur
        fields = [
            'tahun_anggaran',
            'kegiatan',
            'anggaran',
            'sumber_anggaran',
            'ketua_tpk',
            'nomor_sk',
            'file_sk',
            'file_sk_tpk',
            'file_rab',
            'file_lpj',
            'file_surat_pengantar',
            'file_berita_acara',
        ]
        widgets = {
            'kegiatan': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nama kegiatan infrastruktur',
            }),
            'anggaran': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'min': '0',
            }),
            'sumber_anggaran':  forms.Select(attrs={'class': 'form-select'}),
            'ketua_tpk':        forms.TextInput(attrs={'class': 'form-control'}),
            'nomor_sk':         forms.TextInput(attrs={'class': 'form-control', 'placeholder': '001/SK/2025'}),
            'file_sk':          forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx'}),
            'file_sk_tpk':      forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx'}),
            'file_rab':         forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx'}),
            'file_lpj':         forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx'}),
            'file_surat_pengantar': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx'}),
            'file_berita_acara':    forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx'}),
        }
        labels = {
            'kegiatan':       'Nama Kegiatan',
            'anggaran':       'Anggaran (Rp)',
            'sumber_anggaran': 'Sumber Anggaran',
            'ketua_tpk':      'Ketua TPK',
            'nomor_sk':       'Nomor SK',
            'file_sk':        'File SK',
            'file_sk_tpk':    'File SK TPK',
            'file_rab':       'File RAB',
            'file_lpj':       'File LPJ',
            'file_surat_pengantar': 'Surat Pengantar',
            'file_berita_acara':    'Berita Acara',
        }

    def clean_tahun_anggaran(self):
        return int(self.cleaned_data['tahun_anggaran'])


# ──────────────────────────────────────────
# Form untuk tiap baris detail infrastruktur
# ──────────────────────────────────────────

class InfrastrukturDetailForm(forms.ModelForm):
    class Meta:
        model  = InfrastrukturDetail
        fields = ['jenis', 'lokasi', 'volume', 'keterangan_lainnya']
        widgets = {
            'jenis':  forms.Select(attrs={'class': 'form-select'}),
            'lokasi': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lokasi pekerjaan'}),
            'volume': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 200 meter'}),
            'keterangan_lainnya': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Wajib diisi jika jenis = Lainnya',
            }),
        }
        labels = {
            'jenis':              'Jenis Infrastruktur',
            'lokasi':             'Lokasi',
            'volume':             'Volume',
            'keterangan_lainnya': 'Keterangan',
        }


# ──────────────────────────────────────────
# Formset — gabungkan detail ke parent
# ──────────────────────────────────────────

InfrastrukturDetailFormSet = inlineformset_factory(
    Infrastruktur,
    InfrastrukturDetail,
    form=InfrastrukturDetailForm,
    extra=1,            # 1 baris kosong default
    min_num=1,          # minimal 1 detail wajib diisi
    validate_min=True,
    can_delete=True,    # user bisa hapus baris
    exclude=['id'],     # Exclude ID field dari form rendering
)

class InfrastrukturFotoForm(forms.ModelForm):
    class Meta:
        model  = InfrastrukturFoto
        fields = ['tahap', 'foto']
        widgets = {
            'tahap': forms.Select(attrs={'class': 'form-select'}),
            'foto':  forms.FileInput(attrs={'class': 'form-control'}),
        }

InfrastrukturFotoFormSet = inlineformset_factory(
    Infrastruktur,
    InfrastrukturFoto,
    form=InfrastrukturFotoForm,
    extra=1,
    can_delete=True,
    exclude=['id'],     # Exclude ID field dari form rendering
)