"""Only EX5 files in an operator-configured private folder can be downloaded."""
from pathlib import Path

from django.conf import settings
from django.urls import reverse

from .models import EAProgram

RESOURCES = {
    "auth-bridge": {
        "title": "MOCONIX 인증 도우미", "type": "helper", "filename": "MOCONIX_AuthBridge.ex5",
        "description": "지표 실행에 필요한 계좌 인증 프로그램입니다. 주문 기능은 없습니다.",
    },
    "rsi-arrow": {
        "title": "RSIArrow 인디케이터", "type": "indicator", "filename": "MOCONIX_RSIArrow.ex5",
        "description": "RSI 밴드 복귀 신호를 화살표로 표시합니다. 현재 봉의 신호는 시세에 따라 바뀔 수 있습니다.",
    },
}


def resource_path(resource_id):
    metadata = RESOURCES.get(resource_id)
    configured = getattr(settings, "MOCONIX_UTILITY_DOWNLOAD_DIR", "")
    if not metadata or not configured:
        return None
    root = Path(configured).resolve()
    path = root / metadata["filename"]
    if path.is_symlink() or not path.is_file() or path.resolve().parent != root:
        return None
    if not EAProgram.objects.filter(code="moconix-rsi-arrow-v1", program_type="indicator", is_active=True).exists():
        return None
    return path


def available_resources():
    return [{"id": key, **metadata, "download_url": reverse("utility-download", args=[key])}
            for key, metadata in RESOURCES.items() if resource_path(key) is not None]
