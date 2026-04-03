from django.urls import path
from django.views.generic import RedirectView
from ekbang.views.auth import (
    login_view, logout_view, buat_akun_desa,desa_create,
    dashboard_kecamatan, dashboard_desa, review_list,notifikasi_count,kirim_peringatan_masal
)

urlpatterns = [
    path('', RedirectView.as_view(url='/login/'), name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('buat-akun-desa/', buat_akun_desa, name='buat_akun_desa'),
    path('dashboard/kecamatan/', dashboard_kecamatan, name='dashboard_kecamatan'),
    path('dashboard/desa/', dashboard_desa, name='dashboard_desa'),
    path('review/', review_list, name='review_list'),
    path('dashboard/desa_create/', desa_create, name='desa_create'),
    path('api/notifikasi/', notifikasi_count, name='notifikasi_count'),
    path('kirim-peringatan-masal/', kirim_peringatan_masal, name='kirim_peringatan_masal'),
]