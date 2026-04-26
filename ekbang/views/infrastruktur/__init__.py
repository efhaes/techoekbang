# ekbang/views/infrastruktur/__init__.py
from .desa import (
    infrastruktur_list,
    infrastruktur_create,
    infrastruktur_edit,
    infrastruktur_detail,
    infrastruktur_submit,
    infrastruktur_delete,
)
from .kecamatan import (
    infrastruktur_list_kecamatan,
    infrastruktur_detail_kecamatan,
    infrastruktur_verifikasi,
    infrastruktur_filter_api,
)