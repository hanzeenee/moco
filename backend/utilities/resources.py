"""Only EX5 files in an operator-configured private folder can be downloaded."""
from pathlib import Path

from django.conf import settings
from django.urls import reverse

from .models import EAProgram

RESOURCES = {
    "breakout-martingale": {
        "title": "양방향 돌파·마틴게일 EA", "type": "ea", "filename": "MOCONIX_BreakoutMartingale.ex5",
        "program": "moconix-breakout-martingale-v1",
        "description": "양방향 예약주문과 마틴게일로 진입하고 바스켓 익절을 관리합니다.",
        "note": "헤징 계좌 전용 · 같은 종목의 기존 포지션과 예약주문도 관리합니다.",
    },
    "ut-bot": {
        "title": "UT Bot 시그널 인디케이터", "type": "indicator", "filename": "MOCONIX_UTBot.ex5",
        "program": "moconix-utbot-v1",
        "description": "ATR 기반 매수·매도 신호를 차트에 표시합니다.",
        "note": "인증 EA 필요 · 현재 봉의 신호는 시세에 따라 바뀔 수 있습니다.",
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
