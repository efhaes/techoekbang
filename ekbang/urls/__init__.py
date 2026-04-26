from django.urls import path, include

urlpatterns = [
    path('', include('ekbang.urls.auth')),
    path('bumdes/', include('ekbang.urls.bumdes')),
    path('bltdd/', include('ekbang.urls.bltdd')),
    path('infrastruktur/', include('ekbang.urls.infrastruktur')),
    path('koperasi/', include('ekbang.urls.koprasi')),
    path('ketahanan-pangan/', include('ekbang.urls.ketahanan_pangan')),
    path('dokumen/', include('ekbang.urls.dokumen'))
]