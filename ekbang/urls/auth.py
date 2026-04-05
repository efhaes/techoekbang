from django.urls import path
from django.views.generic import RedirectView
from ekbang.views.auth import (
    login_view, logout_view, buat_akun_desa, desa_create,
    dashboard_kecamatan, dashboard_desa, review_list, notifikasi_count,
    kirim_peringatan_masal, verifikasi_email, edit_akun_desa, hapus_akun_desa,
    akun_desa_list,            # <--- NEW: Import ini
    kirim_ulang_verifikasi     # <--- NEW: Import ini
)

urlpatterns = [
    path('', RedirectView.as_view(url='/login/'), name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    
    # MANAJEMEN AKUN DESA
    path('akun-desa/', akun_desa_list, name='akun_desa_list'),
    path('akun-desa/buat/', buat_akun_desa, name='buat_akun_desa'),
    path('akun-desa/<int:user_id>/edit/', edit_akun_desa, name='edit_akun_desa'),
    path('akun-desa/<int:user_id>/hapus/', hapus_akun_desa, name='hapus_akun_desa'),
    path('akun-desa/<int:user_id>/resend-verifikasi/', kirim_ulang_verifikasi, name='kirim_ulang_verifikasi'),
    # DASHBOARD & LAINNYA
    path('dashboard/kecamatan/', dashboard_kecamatan, name='dashboard_kecamatan'),
    path('dashboard/desa/', dashboard_desa, name='dashboard_desa'),
    path('review/', review_list, name='review_list'),
    path('dashboard/desa_create/', desa_create, name='desa_create'),
    path('api/notifikasi/', notifikasi_count, name='notifikasi_count'),
    path('kirim-peringatan-masal/', kirim_peringatan_masal, name='kirim_peringatan_masal'),
    path('verifikasi-email/<uidb64>/<token>/', verifikasi_email, name='verifikasi_email'),
]