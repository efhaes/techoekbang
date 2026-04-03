# ekbang/urls/koperasi.py  ← bukan koprasi
from django.urls import path
from ekbang.views.koprasi import (
    koperasi_list, koperasi_create, koperasi_edit,
    koperasi_detail, koperasi_submit, koperasi_delete,
    koperasi_list_kecamatan, koperasi_detail_kecamatan,
    koperasi_verifikasi, koperasi_filter_api,
)

urlpatterns = [
    path('', koperasi_list, name='koperasi_list'),
    path('tambah/', koperasi_create, name='koperasi_create'),
    path('<int:pk>/edit/', koperasi_edit, name='koperasi_edit'),
    path('<int:pk>/detail/', koperasi_detail, name='koperasi_detail'),
    path('<int:pk>/submit/', koperasi_submit, name='koperasi_submit'),
    path('<int:pk>/delete/', koperasi_delete, name='koperasi_delete'),
    path('kecamatan/', koperasi_list_kecamatan, name='koperasi_list_kecamatan'),
    path('kecamatan/<int:pk>/', koperasi_detail_kecamatan, name='koperasi_detail_kecamatan'),
    path('kecamatan/<int:pk>/verifikasi/', koperasi_verifikasi, name='koperasi_verifikasi'),
    path('kecamatan/filter/', koperasi_filter_api, name='koperasi_filter_api'),
]