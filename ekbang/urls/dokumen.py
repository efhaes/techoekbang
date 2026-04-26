from django.urls import path
from ekbang.views.dokumen import template_dokumen, download_template

urlpatterns = [
    path('', template_dokumen, name='template_dokumen'),
    path('<str:jenis>/download/', download_template, name='download_template'),
]