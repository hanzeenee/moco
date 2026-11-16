"""Only EX5 files in an operator-configured private folder can be downloaded."""
from pathlib import Path

from django.conf import settings
from django.urls import reverse

from .models import EAProgram

RESOURCES = {
    "sma-cross-ea": {
        "title": "SMA 크로스 EA", "type": "ea", "filename": "MOCO_EA_SMA_Cross.ex5",
        "program": "moconix-sma-cross-ea",
        "description": "SMA 교차 확정 후 매매하며, 반대 신호에서 청산·반전합니다.",
    },
    "sma-cross-indicator": {
        "title": "SMA 크로스 화살표 인디케이터", "type": "indicator", "filename": "MOCO_indi_SMA_Cross.ex5",
        "program": "moconix-sma-cross-arrow",
        "description": "SMA 교차가 확정된 봉에 매수·매도 화살표를 표시합니다.",
    },
    "auth-bridge": {
        "title": "인디케이터 인증 EA", "type": "helper", "filename": "MOCONIX_AuthBridge.ex5",
        "description": "인디케이터 실행을 위한 계좌 인증용 EA입니다. 주문 기능은 없습니다.",
    },
}


def resource_path(resource_id):
    metadata = RESOURCES.get(resource_id)
    configured = getattr(settings, "MOCONIX_UTILITY_DOWNLOAD_DIR", "")
    if not metadata or not configured:
        return None
    if metadata.get("program") and not EAProgram.objects.filter(
        code=metadata["program"], program_type=metadata["type"], is_active=True,
    ).exists():
        return None
    root = Path(configured).resolve()
    path = root / metadata["filename"]
    if path.is_symlink() or not path.is_file() or path.resolve().parent != root:
        return None
    return path


def available_resources():
    return [{"id": key, **{field: value for field, value in metadata.items() if field != "program"}, "download_url": reverse("utility-download", args=[key])}
            for key, metadata in RESOURCES.items() if resource_path(key) is not None]
