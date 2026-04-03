from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import datetime


# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────

def tahun_sekarang():
    return datetime.date.today().year


class UploadPath:
    """
    Hasil path: modul/subfolder/<desa_id>/<tahun_anggaran>/<filename>
    """
    def __init__(self, modul, subfolder):
        self.modul = modul
        self.subfolder = subfolder

    def __call__(self, instance, filename):
        # kalau model utama (punya desa langsung)
        if hasattr(instance, 'desa_id'):
            desa_id = instance.desa_id
            tahun   = instance.tahun_anggaran
        else:
            # kalau child (contoh: InfrastrukturFoto)
            desa_id = instance.infrastruktur.desa_id
            tahun   = instance.infrastruktur.tahun_anggaran

        return f'{self.modul}/{self.subfolder}/{desa_id}/{tahun}/{filename}'

    def deconstruct(self):
        return (
            'ekbang.models.UploadPath',
            [self.modul, self.subfolder],
            {},
        )


# ─────────────────────────────────────────
# STATUS CHOICES
# ─────────────────────────────────────────

STATUS_CHOICES = [
    ('draft',     'Draft'),
    ('diajukan',  'Diajukan'),
    ('disetujui', 'Disetujui'),
    ('ditolak',   'Ditolak'),
]


# ─────────────────────────────────────────
# MASTER DESA
# ─────────────────────────────────────────

class Desa(models.Model):
    nama      = models.CharField(max_length=100)
    kecamatan = models.CharField(max_length=100)

    class Meta:
        verbose_name        = 'Desa'
        verbose_name_plural = 'Desa'
        ordering            = ['nama']

    def __str__(self):
        return f'{self.nama} — {self.kecamatan}'


# ─────────────────────────────────────────
# USER PROFILE
# ─────────────────────────────────────────

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin_kecamatan', 'Admin Kecamatan'),
        ('admin_desa',      'Admin Desa'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    desa = models.ForeignKey(
        Desa,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text='Wajib diisi jika role Admin Desa',
    )

    class Meta:
        verbose_name        = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f'{self.user.username} ({self.get_role_display()})'

    def is_kecamatan(self):
        return self.role == 'admin_kecamatan'

    def is_desa(self):
        return self.role == 'admin_desa'


# ─────────────────────────────────────────
# BASE PERMOHONAN (abstract)
# ─────────────────────────────────────────

class BasePermohonan(models.Model):
    desa           = models.ForeignKey(Desa, on_delete=models.CASCADE)
    tahun_anggaran = models.PositiveIntegerField(default=tahun_sekarang)
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    # Nomor & file SK — file_sk di-override tiap child
    nomor_sk = models.CharField(max_length=100, blank=True)
    file_sk  = models.FileField(upload_to='dokumen/sk/', null=True, blank=True)

    # Pengajuan
    diajukan_oleh    = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='%(class)s_diajukan',
    )
    tanggal_diajukan = models.DateTimeField(null=True, blank=True)

    # Verifikasi
    diverifikasi_oleh  = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='%(class)s_diverifikasi',
    )
    tanggal_verifikasi = models.DateTimeField(null=True, blank=True)
    catatan_verifikasi = models.TextField(blank=True)

    # Dokumen umum
    file_surat_pengantar = models.FileField(
        upload_to='dokumen/surat_pengantar/',
        null=True, blank=True,
    )
    file_berita_acara = models.FileField(
        upload_to='dokumen/berita_acara/',
        null=True, blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']
        indexes  = [
            models.Index(fields=['tahun_anggaran']),
            models.Index(fields=['status']),
        ]

    def ajukan(self, user):
        if self.status != 'draft':
            raise ValidationError('Hanya draft yang bisa diajukan.')
        self.status           = 'diajukan'
        self.diajukan_oleh    = user
        self.tanggal_diajukan = datetime.datetime.now()
        self.save()

    def verifikasi(self, user, status, catatan=None):
        if self.status != 'diajukan':
            raise ValidationError('Data belum diajukan.')
        if status not in ('disetujui', 'ditolak'):
            raise ValidationError('Status tidak valid.')
        self.status             = status
        self.diverifikasi_oleh  = user
        self.tanggal_verifikasi = datetime.datetime.now()
        self.catatan_verifikasi = catatan or ''
        self.save()


# ─────────────────────────────────────────
# BUMDes
# ─────────────────────────────────────────

class Bumdes(BasePermohonan):
    file_sk = models.FileField(
        upload_to=UploadPath('bumdes', 'sk'),
        null=True, blank=True,
    )

    nama_bumdes    = models.CharField(max_length=150)
    nomor_perdes   = models.CharField(max_length=50, blank=True)
    tanggal_perdes = models.DateField(null=True, blank=True)

    # Pengurus
    direktur          = models.CharField(max_length=100, blank=True)
    komisaris         = models.CharField(max_length=100, blank=True)
    sekretaris        = models.CharField(max_length=100, blank=True)
    bendahara         = models.CharField(max_length=100, blank=True)
    ketua_unit_usaha  = models.CharField(max_length=100, blank=True)

    # Pengawas
    ketua_pengawas     = models.CharField(max_length=100, blank=True)
    anggota_pengawas_1 = models.CharField(max_length=100, blank=True)
    anggota_pengawas_2 = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name        = 'BUMDes'
        verbose_name_plural = 'BUMDes'
        ordering            = ['-created_at']

    def __str__(self):
        return f'{self.nama_bumdes} — {self.desa} [{self.get_status_display()}]'


# ─────────────────────────────────────────
# BLT Dana Desa
# ─────────────────────────────────────────

class BLTDD(BasePermohonan):
    file_sk = models.FileField(
        upload_to=UploadPath('bltdd', 'sk'),
        null=True, blank=True,
    )

    jumlah_kpm           = models.PositiveIntegerField()
    nominal_per_bulan    = models.DecimalField(max_digits=12, decimal_places=2)
    jumlah_bulan = models.IntegerField(default=1)
    jumlah_total_terima  = models.DecimalField(max_digits=15, decimal_places=2)
    lpj_bulan_sebelumnya = models.FileField(
        upload_to=UploadPath('bltdd', 'lpj_sebelumnya'),
        null=True, blank=True,
    )

    class Meta:
        verbose_name        = 'BLT Dana Desa'
        verbose_name_plural = 'BLT Dana Desa'
        ordering            = ['-created_at']

    def __str__(self):
        return f'BLT-DD {self.desa} [{self.get_status_display()}]'


# ─────────────────────────────────────────
# INFRASTRUKTUR
# ─────────────────────────────────────────

class Infrastruktur(BasePermohonan):
    SUMBER_CHOICES = [
        ('APBD1',   'APBD 1'),
        ('APBD2',   'APBD 2'),
        ('APBN',    'APBN'),
        ('Lainnya', 'Lainnya'),
    ]

    file_sk = models.FileField(
        upload_to=UploadPath('infrastruktur', 'sk'),
        null=True, blank=True,
    )

    kegiatan        = models.CharField(max_length=150)
    anggaran        = models.DecimalField(max_digits=15, decimal_places=2)
    sumber_anggaran = models.CharField(max_length=20, choices=SUMBER_CHOICES)
    ketua_tpk       = models.CharField(max_length=100, blank=True)

    file_sk_tpk = models.FileField(
        upload_to=UploadPath('infrastruktur', 'sk_tpk'),
        null=True, blank=True,
    )
    file_rab = models.FileField(
        upload_to=UploadPath('infrastruktur', 'rab'),
        null=True, blank=True,
    )
    file_lpj = models.FileField(
        upload_to=UploadPath('infrastruktur', 'lpj'),
        null=True, blank=True,
    )

    class Meta:
        verbose_name        = 'Infrastruktur'
        verbose_name_plural = 'Infrastruktur'
        ordering            = ['-created_at']

    def __str__(self):
        return f'Infrastruktur {self.desa} — {self.kegiatan} [{self.get_status_display()}]'


class InfrastrukturDetail(models.Model):
    JENIS_CHOICES = [
        ('jalan_lingkungan', 'Jalan Lingkungan'),
        ('jalan_desa',       'Jalan Desa'),
        ('bangunan',         'Bangunan'),
        ('jembatan',         'Jembatan'),
        ('lainnya',          'Lainnya'),
    ]

    infrastruktur      = models.ForeignKey(Infrastruktur, on_delete=models.CASCADE, related_name='details')
    jenis              = models.CharField(max_length=50, choices=JENIS_CHOICES)
    lokasi             = models.TextField()
    volume             = models.CharField(max_length=100)
    keterangan_lainnya = models.CharField(max_length=150, blank=True)

    class Meta:
        verbose_name        = 'Detail Infrastruktur'
        verbose_name_plural = 'Detail Infrastruktur'

    def clean(self):
        if self.jenis == 'lainnya' and not self.keterangan_lainnya:
            raise ValidationError("Keterangan wajib diisi jika pilih 'lainnya'.")

    def __str__(self):
        return f'{self.get_jenis_display()} — {self.lokasi}'


class InfrastrukturFoto(models.Model):
    TAHAP_CHOICES = [
        ('awal',   'Awal'),
        ('tengah', 'Tengah'),
        ('akhir',  'Akhir'),
    ]

    infrastruktur = models.ForeignKey(Infrastruktur, on_delete=models.CASCADE, related_name='fotos')
    tahap         = models.CharField(max_length=10, choices=TAHAP_CHOICES)
    foto          = models.ImageField(upload_to=UploadPath('infrastruktur', 'foto'))

    class Meta:
        verbose_name        = 'Foto Infrastruktur'
        verbose_name_plural = 'Foto Infrastruktur'

    def __str__(self):
        return f'{self.get_tahap_display()} — {self.infrastruktur}'


# ─────────────────────────────────────────
# KOPERASI
# ─────────────────────────────────────────

class Koperasi(BasePermohonan):
    file_sk = models.FileField(
        upload_to=UploadPath('koperasi', 'sk'),
        null=True, blank=True,
    )

    nama_koperasi      = models.CharField(max_length=150)
    tanggal_sk         = models.DateField(null=True, blank=True)
    akta_notaris_nomor = models.CharField(max_length=100, blank=True)

    # Pengurus
    ketua                = models.CharField(max_length=100, blank=True)
    wakil_bidang_anggota = models.CharField(max_length=100, blank=True)
    wakil_bidang_usaha   = models.CharField(max_length=100, blank=True)
    sekretaris           = models.CharField(max_length=100, blank=True)
    bendahara            = models.CharField(max_length=100, blank=True)

    # Pengawas
    ketua_pengawas     = models.CharField(max_length=100, blank=True)
    anggota_pengawas_1 = models.CharField(max_length=100, blank=True)
    anggota_pengawas_2 = models.CharField(max_length=100, blank=True)

    file_rapbk = models.FileField(
        upload_to=UploadPath('koperasi', 'rapbk'),
        null=True, blank=True,
    )

    class Meta:
        verbose_name        = 'Koperasi'
        verbose_name_plural = 'Koperasi'
        ordering            = ['-created_at']

    def __str__(self):
        return f'{self.nama_koperasi} — {self.desa} [{self.get_status_display()}]'




# ─────────────────────────────────────────
# KETAHANAN PANGAN
# ─────────────────────────────────────────

class KetahananPangan(BasePermohonan):
    nama_kelompok = models.CharField(max_length=150)
    nomor_sk      = models.CharField(max_length=50, blank=True)
    tanggal_sk    = models.DateField(null=True, blank=True)

    pembiayaan_anggaran = models.DecimalField(
        max_digits=15, decimal_places=2,
        null=True, blank=True
    )

    ketua = models.CharField(max_length=100, blank=True)

    # ✅ checkbox (boolean)
    usaha_pertanian   = models.BooleanField(default=False)
    usaha_peternakan  = models.BooleanField(default=False)
    usaha_perladangan = models.BooleanField(default=False)
    usaha_perdagangan = models.BooleanField(default=False)
    usaha_perikanan   = models.BooleanField(default=False)

    # ✅ tambahan "lainnya"
    usaha_lainnya = models.CharField(
        max_length=150,
        blank=True,
        help_text="Isi jika jenis usaha tidak tersedia"
    )

    proposal = models.FileField(
        upload_to=UploadPath('ketahanan', 'proposal'),
        null=True, blank=True,
    )

    file_lpj_ketahanan = models.FileField(
        upload_to=UploadPath('ketahanan', 'lpj'),
        null=True, blank=True,
    )

    class Meta:
        verbose_name = 'Ketahanan Pangan'
        verbose_name_plural = 'Ketahanan Pangan'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.nama_kelompok} — {self.desa} [{self.get_status_display()}]'