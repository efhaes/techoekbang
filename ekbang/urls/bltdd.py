# ekbang/urls/bltdd.py
from django.urls import path
from ekbang.views.bltdd import (
    bltdd_list, bltdd_create, bltdd_edit,
    bltdd_detail, bltdd_submit, bltdd_delete,
    bltdd_list_kecamatan, bltdd_detail_kecamatan,
    bltdd_verifikasi, bltdd_filter_api,
)

urlpatterns = [
    path('', bltdd_list, name='bltdd_list'),
    path('tambah/', bltdd_create, name='bltdd_create'),
    path('<int:pk>/edit/', bltdd_edit, name='bltdd_edit'),
    path('<int:pk>/detail/', bltdd_detail, name='bltdd_detail'),
    path('<int:pk>/submit/', bltdd_submit, name='bltdd_submit'),
    path('<int:pk>/delete/', bltdd_delete, name='bltdd_delete'),
    path('kecamatan/', bltdd_list_kecamatan, name='bltdd_list_kecamatan'),
    path('kecamatan/<int:pk>/', bltdd_detail_kecamatan, name='bltdd_detail_kecamatan'),
    path('kecamatan/<int:pk>/verifikasi/', bltdd_verifikasi, name='bltdd_verifikasi'),
    path('kecamatan/filter/', bltdd_filter_api, name='bltdd_filter_api'),
]