# ekbang/urls/ketahanan.py  ← bukan ketahanan_pangan
from django.urls import path
from ekbang.views.ketahanan_pangan import (
    ketahanan_pangan_list, ketahanan_pangan_create, ketahanan_pangan_edit,
    ketahanan_pangan_detail, ketahanan_pangan_submit, ketahanan_pangan_delete,
    ketahanan_pangan_list_kecamatan, ketahanan_pangan_detail_kecamatan,
    ketahanan_pangan_verifikasi, ketahanan_pangan_filter_api,
)

urlpatterns = [
    path('', ketahanan_pangan_list, name='ketahanan_pangan_list'),
    path('tambah/', ketahanan_pangan_create, name='ketahanan_pangan_create'),
    path('<int:pk>/edit/', ketahanan_pangan_edit, name='ketahanan_pangan_edit'),
    path('<int:pk>/detail/', ketahanan_pangan_detail, name='ketahanan_pangan_detail'),
    path('<int:pk>/submit/', ketahanan_pangan_submit, name='ketahanan_pangan_submit'),
    path('<int:pk>/delete/', ketahanan_pangan_delete, name='ketahanan_pangan_delete'),
    path('kecamatan/', ketahanan_pangan_list_kecamatan, name='ketahanan_pangan_list_kecamatan'),
    path('kecamatan/<int:pk>/', ketahanan_pangan_detail_kecamatan, name='ketahanan_pangan_detail_kecamatan'),
    path('kecamatan/<int:pk>/verifikasi/', ketahanan_pangan_verifikasi, name='ketahanan_pangan_verifikasi'),
    path('kecamatan/filter/', ketahanan_pangan_filter_api, name='ketahanan_pangan_filter_api'),
]