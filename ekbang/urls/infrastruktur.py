# ekbang/urls/infrastruktur.py
from django.urls import path
from ekbang.views.infrastruktur import (
    infrastruktur_list, infrastruktur_create, infrastruktur_edit,
    infrastruktur_detail, infrastruktur_submit, infrastruktur_delete,
    infrastruktur_list_kecamatan, infrastruktur_detail_kecamatan,
    infrastruktur_verifikasi, infrastruktur_filter_api,
)

urlpatterns = [
    path('', infrastruktur_list, name='infrastruktur_list'),
    path('tambah/', infrastruktur_create, name='infrastruktur_create'),
    path('<int:pk>/edit/', infrastruktur_edit, name='infrastruktur_edit'),
    path('<int:pk>/detail/', infrastruktur_detail, name='infrastruktur_detail'),
    path('<int:pk>/submit/', infrastruktur_submit, name='infrastruktur_submit'),
    path('<int:pk>/delete/', infrastruktur_delete, name='infrastruktur_delete'),
    path('kecamatan/', infrastruktur_list_kecamatan, name='infrastruktur_list_kecamatan'),
    path('kecamatan/<int:pk>/', infrastruktur_detail_kecamatan, name='infrastruktur_detail_kecamatan'),
    path('kecamatan/<int:pk>/verifikasi/', infrastruktur_verifikasi, name='infrastruktur_verifikasi'),
    path('kecamatan/filter/', infrastruktur_filter_api, name='infrastruktur_filter_api'),
]