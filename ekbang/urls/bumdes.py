# ekbang/urls/bumdes.py
from django.urls import path
from ekbang.views.bumdes import (
    bumdes_list, bumdes_create, bumdes_edit,
    bumdes_detail, bumdes_submit, bumdes_delete,
    bumdes_list_kecamatan, bumdes_detail_kecamatan,
    bumdes_verifikasi, bumdes_filter_api,
)

urlpatterns = [
    path('', bumdes_list, name='bumdes_list'),
    path('tambah/', bumdes_create, name='bumdes_create'),
    path('<int:pk>/edit/', bumdes_edit, name='bumdes_edit'),
    path('<int:pk>/detail/', bumdes_detail, name='bumdes_detail'),
    path('<int:pk>/submit/', bumdes_submit, name='bumdes_submit'),
    path('<int:pk>/delete/', bumdes_delete, name='bumdes_delete'),
    path('kecamatan/', bumdes_list_kecamatan, name='bumdes_list_kecamatan'),
    path('kecamatan/<int:pk>/', bumdes_detail_kecamatan, name='bumdes_detail_kecamatan'),
    path('kecamatan/<int:pk>/verifikasi/', bumdes_verifikasi, name='bumdes_verifikasi'),
    path('kecamatan/filter/', bumdes_filter_api, name='bumdes_filter_api'),
]