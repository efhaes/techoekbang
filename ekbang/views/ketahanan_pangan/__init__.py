# ekbang/views/ketahanan/__init__.py
from .desa import (
    ketahanan_pangan_list,
    ketahanan_pangan_create,
    ketahanan_pangan_edit,
    ketahanan_pangan_detail,
    ketahanan_pangan_submit,
    ketahanan_pangan_delete,
)
from .kecamatan import (
    ketahanan_pangan_list_kecamatan,
    ketahanan_pangan_detail_kecamatan,
    ketahanan_pangan_verifikasi,
    ketahanan_pangan_filter_api,
)