from django.contrib import admin
from .models import *


# ─────────────────────────────────────────
# USER PROFILE
# ─────────────────────────────────────────

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'desa')
    list_filter = ('role',)
    search_fields = ('user__username',)


# ─────────────────────────────────────────
# DESA
# ─────────────────────────────────────────

@admin.register(Desa)
class DesaAdmin(admin.ModelAdmin):
    list_display = ('nama', 'kecamatan')
    search_fields = ('nama', 'kecamatan')


# ─────────────────────────────────────────
# BASE ADMIN (REUSABLE)
# ─────────────────────────────────────────

class BasePermohonanAdmin(admin.ModelAdmin):
    list_display = ('desa', 'tahun_anggaran', 'status', 'created_at')
    list_filter = ('tahun_anggaran', 'status', 'desa')
    search_fields = ('nomor_sk',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Informasi Utama', {
            'fields': ('desa', 'tahun_anggaran', 'status')
        }),
        ('SK', {
            'fields': ('nomor_sk', 'file_sk')
        }),
        ('Dokumen Umum', {
            'fields': ('file_surat_pengantar', 'file_berita_acara')
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at')
        }),
    )


# ─────────────────────────────────────────
# BUMDES
# ─────────────────────────────────────────

@admin.register(Bumdes)
class BumdesAdmin(BasePermohonanAdmin):
    list_display = ('nama_bumdes', 'desa', 'status', 'created_at')

    fieldsets = BasePermohonanAdmin.fieldsets + (
        ('BUMDes', {
            'fields': ('nama_bumdes', 'nomor_perdes', 'tanggal_perdes')
        }),
        ('Pengurus', {
            'fields': ('direktur', 'komisaris', 'sekretaris', 'bendahara', 'ketua_unit_usaha')
        }),
        ('Pengawas', {
            'fields': ('ketua_pengawas', 'anggota_pengawas_1', 'anggota_pengawas_2')
        }),
    )


# ─────────────────────────────────────────
# BLT DD
# ─────────────────────────────────────────

@admin.register(BLTDD)
class BLTDDAdmin(BasePermohonanAdmin):
    list_display = ('desa', 'jumlah_kpm', 'jumlah_total_terima', 'status')

    fieldsets = BasePermohonanAdmin.fieldsets + (
        ('BLT', {
            'fields': (
                'jumlah_kpm',
                'nominal_per_bulan',
                'jumlah_total_terima',
                'lpj_bulan_sebelumnya'
            )
        }),
    )


# ─────────────────────────────────────────
# INFRASTRUKTUR INLINE
# ─────────────────────────────────────────

class InfrastrukturDetailInline(admin.TabularInline):
    model = InfrastrukturDetail
    extra = 1


class InfrastrukturFotoInline(admin.TabularInline):
    model = InfrastrukturFoto
    extra = 1
    max_num = 3


# ─────────────────────────────────────────
# INFRASTRUKTUR
# ─────────────────────────────────────────

@admin.register(Infrastruktur)
class InfrastrukturAdmin(BasePermohonanAdmin):
    list_display = ('kegiatan', 'desa', 'anggaran', 'status')

    inlines = [InfrastrukturDetailInline, InfrastrukturFotoInline]

    fieldsets = BasePermohonanAdmin.fieldsets + (
        ('Infrastruktur', {
            'fields': (
                'kegiatan',
                'anggaran',
                'sumber_anggaran',
                'ketua_tpk'
            )
        }),
        ('Dokumen Infrastruktur', {
            'fields': (
                'file_sk_tpk',
                'file_rab',
                'file_lpj'
            )
        }),
    )


# ─────────────────────────────────────────
# KOPERASI
# ─────────────────────────────────────────

@admin.register(Koperasi)
class KoperasiAdmin(BasePermohonanAdmin):
    list_display = ('nama_koperasi', 'desa', 'status')

    fieldsets = BasePermohonanAdmin.fieldsets + (
        ('Koperasi', {
            'fields': (
                'nama_koperasi',
                'tanggal_sk',
                'akta_notaris_nomor'
            )
        }),
        ('Pengurus', {
            'fields': (
                'ketua',
                'wakil_bidang_anggota',
                'wakil_bidang_usaha',
                'sekretaris',
                'bendahara'
            )
        }),
        ('Pengawas', {
            'fields': (
                'ketua_pengawas',
                'anggota_pengawas_1',
                'anggota_pengawas_2'
            )
        }),
        ('Dokumen', {
            'fields': ('file_rapbk',)
        }),
    )


# ─────────────────────────────────────────
# JENIS USAHA
# ─────────────────────────────────────────




# ─────────────────────────────────────────
# KETAHANAN PANGAN
# ─────────────────────────────────────────

@admin.register(KetahananPangan)
class KetahananPanganAdmin(BasePermohonanAdmin):
    list_display = ('nama_kelompok', 'desa', 'status')

    fieldsets = BasePermohonanAdmin.fieldsets + (
        ('Ketahanan Pangan', {
            'fields': (
                'nama_kelompok',
                'tanggal_sk',
                'pembiayaan_anggaran',
                'ketua',
                'jenis_usaha'
            )
        }),
        ('Dokumen', {
            'fields': (
                'proposal',
                'file_lpj_ketahanan'
            )
        }),
    )