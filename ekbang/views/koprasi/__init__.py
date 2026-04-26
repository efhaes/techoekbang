# ekbang/views/koperasi/__init__.py
from .desa import (
    koperasi_list,
    koperasi_create,
    koperasi_edit,
    koperasi_detail,
    koperasi_submit,
    koperasi_delete,
)
from .kecamatan import (
    koperasi_list_kecamatan,
    koperasi_detail_kecamatan,
    koperasi_verifikasi,
    koperasi_filter_api,
)