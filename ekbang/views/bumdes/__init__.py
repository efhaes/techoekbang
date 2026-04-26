# ekbang/views/bumdes/__init__.py
from .desa import (
    bumdes_list,
    bumdes_create,
    bumdes_edit,
    bumdes_detail,
    bumdes_submit,
    bumdes_delete,
)
from .kecamatan import (
    bumdes_list_kecamatan,
    bumdes_detail_kecamatan,
    bumdes_verifikasi,       # bukan bumdes_acc + bumdes_tolak
    bumdes_filter_api,
)